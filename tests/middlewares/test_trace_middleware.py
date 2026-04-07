from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middlewares.trace import TRACE_HEADER, trace_middleware
from app.schemas.response import Response


def test_trace_middleware_echoes_request_header():
    app = FastAPI()
    app.middleware("http")(trace_middleware)

    @app.get("/ping")
    def ping():
        return Response.success(data={"pong": True}).model_dump()

    client = TestClient(app)
    resp = client.get("/ping", headers={TRACE_HEADER: "trace-123"})
    assert resp.status_code == 200
    assert resp.headers[TRACE_HEADER] == "trace-123"
    assert resp.json()["trace_id"] == "trace-123"


def test_trace_middleware_uses_span_context_when_header_missing(monkeypatch):
    class _SpanContext:
        is_valid = True
        trace_id = int("0123456789abcdef0123456789abcdef", 16)

    class _Span:
        def get_span_context(self):
            return _SpanContext()

    monkeypatch.setattr("app.middlewares.trace.trace.get_current_span", lambda: _Span())

    app = FastAPI()
    app.middleware("http")(trace_middleware)

    @app.get("/ping")
    def ping():
        return Response.success(data={"pong": True}).model_dump()

    client = TestClient(app)
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.headers[TRACE_HEADER] == "0123456789abcdef0123456789abcdef"
    assert resp.json()["trace_id"] == "0123456789abcdef0123456789abcdef"
