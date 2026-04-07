from fastapi import FastAPI

from app.core.tracing import init_tracer


def test_init_tracer_configures_provider_and_instruments(monkeypatch):
    captured = {
        "resource_attributes": None,
        "exporter_endpoint": None,
        "exporter_insecure": None,
        "processor_exporter": None,
        "provider_resource": None,
        "provider_processors": [],
        "set_provider_called": False,
        "instrumented_app": None,
    }

    class _Settings:
        class _App:
            name = "svc-name"

        class _OTel:
            otel_exporter_endpoint = "http://localhost:4317"

        app = _App()
        opentelemetry = _OTel()

    class _FakeResource:
        def __init__(self, *, attributes):
            captured["resource_attributes"] = attributes

    class _FakeExporter:
        def __init__(self, *, endpoint, insecure):
            captured["exporter_endpoint"] = endpoint
            captured["exporter_insecure"] = insecure

    class _FakeSpanProcessor:
        def __init__(self, exporter):
            captured["processor_exporter"] = exporter

    class _FakeProvider:
        def __init__(self, *, resource):
            captured["provider_resource"] = resource

        def add_span_processor(self, processor):
            captured["provider_processors"].append(processor)

    def _fake_set_provider(provider):
        captured["set_provider_called"] = True

    class _FakeInstrumentor:
        @staticmethod
        def instrument_app(app):
            captured["instrumented_app"] = app

    monkeypatch.setattr("app.core.tracing.get_settings", lambda: _Settings())
    monkeypatch.setattr("app.core.tracing.SERVICE_NAME", "service.name", raising=True)
    monkeypatch.setattr("app.core.tracing.Resource", _FakeResource, raising=True)
    monkeypatch.setattr("app.core.tracing.TracerProvider", _FakeProvider, raising=True)
    monkeypatch.setattr("app.core.tracing.OTLPSpanExporter", _FakeExporter, raising=True)
    monkeypatch.setattr("app.core.tracing.BatchSpanProcessor", _FakeSpanProcessor, raising=True)
    monkeypatch.setattr("app.core.tracing.trace.set_tracer_provider", _fake_set_provider, raising=True)
    monkeypatch.setattr("app.core.tracing.FastAPIInstrumentor", _FakeInstrumentor, raising=True)

    app = FastAPI()
    init_tracer(app)

    assert captured["resource_attributes"] == {"service.name": "svc-name"}
    assert captured["exporter_endpoint"] == "http://localhost:4317"
    assert captured["exporter_insecure"] is True
    assert captured["set_provider_called"] is True
    assert captured["instrumented_app"] is app
    assert len(captured["provider_processors"]) == 1
