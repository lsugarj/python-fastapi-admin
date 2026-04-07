from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middlewares.metrics import metrics_middleware


class _Gauge:
    def __init__(self):
        self.inc_calls = 0
        self.dec_calls = 0

    def inc(self):
        self.inc_calls += 1

    def dec(self):
        self.dec_calls += 1


class _LabeledCounter:
    def __init__(self):
        self.labels_calls: list[dict] = []
        self.inc_calls = 0

    def labels(self, **kwargs):
        self.labels_calls.append(kwargs)
        return self

    def inc(self):
        self.inc_calls += 1


class _LabeledHistogram:
    def __init__(self):
        self.labels_calls: list[dict] = []
        self.observe_calls: list[float] = []

    def labels(self, **kwargs):
        self.labels_calls.append(kwargs)
        return self

    def observe(self, value: float):
        self.observe_calls.append(value)


def test_metrics_middleware_records_success(monkeypatch):
    request_count = _LabeledCounter()
    exception_count = _LabeledCounter()
    request_latency = _LabeledHistogram()
    in_progress = _Gauge()

    monkeypatch.setattr("app.middlewares.metrics.REQUEST_COUNT", request_count, raising=True)
    monkeypatch.setattr("app.middlewares.metrics.EXCEPTION_COUNT", exception_count, raising=True)
    monkeypatch.setattr("app.middlewares.metrics.REQUEST_LATENCY", request_latency, raising=True)
    monkeypatch.setattr("app.middlewares.metrics.IN_PROGRESS", in_progress, raising=True)

    app = FastAPI()
    app.middleware("http")(metrics_middleware)

    @app.get("/ok")
    def ok():
        return {"ok": True}

    client = TestClient(app)
    resp = client.get("/ok")
    assert resp.status_code == 200

    assert in_progress.inc_calls == 1
    assert in_progress.dec_calls == 1
    assert request_count.inc_calls == 1
    assert exception_count.inc_calls == 0
    assert request_latency.observe_calls and request_latency.observe_calls[0] >= 0
    assert request_count.labels_calls[0]["method"] == "GET"
    assert request_count.labels_calls[0]["path"] == "/ok"
    assert request_count.labels_calls[0]["status"] == 200


def test_metrics_middleware_records_exception(monkeypatch):
    request_count = _LabeledCounter()
    exception_count = _LabeledCounter()
    request_latency = _LabeledHistogram()
    in_progress = _Gauge()

    monkeypatch.setattr("app.middlewares.metrics.REQUEST_COUNT", request_count, raising=True)
    monkeypatch.setattr("app.middlewares.metrics.EXCEPTION_COUNT", exception_count, raising=True)
    monkeypatch.setattr("app.middlewares.metrics.REQUEST_LATENCY", request_latency, raising=True)
    monkeypatch.setattr("app.middlewares.metrics.IN_PROGRESS", in_progress, raising=True)

    app = FastAPI()
    app.middleware("http")(metrics_middleware)

    @app.get("/boom")
    def boom():
        raise ValueError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/boom")
    assert resp.status_code == 500

    assert in_progress.inc_calls == 1
    assert in_progress.dec_calls == 1
    assert exception_count.inc_calls == 1
    assert request_count.inc_calls == 0
    assert request_latency.observe_calls and request_latency.observe_calls[0] >= 0
    assert exception_count.labels_calls[0]["method"] == "GET"
    assert exception_count.labels_calls[0]["path"] == "/boom"
    assert exception_count.labels_calls[0]["exception"] == "ValueError"
