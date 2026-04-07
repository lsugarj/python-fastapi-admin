from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middlewares.logging import logging_middleware
from app.schemas.response import Response


class _CapturingLogger:
    def __init__(self):
        self.calls: list[dict] = []

    def info(self, msg, extra=None):
        self.calls.append({"msg": msg, "extra": extra})


def test_logging_middleware_emits_access_log(monkeypatch):
    cap = _CapturingLogger()
    monkeypatch.setattr("app.middlewares.logging.logger", cap, raising=True)

    app = FastAPI()
    app.middleware("http")(logging_middleware)

    @app.get("/hello")
    async def hello(request: Request):
        request.state.user_id = 99
        return Response.success(data={"hello": "world"}).model_dump()

    client = TestClient(app)
    resp = client.get("/hello")
    assert resp.status_code == 200

    assert len(cap.calls) == 1
    call = cap.calls[0]
    assert call["msg"] == "access_log"
    assert call["extra"]["method"] == "GET"
    assert call["extra"]["path"] == "/hello"
    assert call["extra"]["status"] == 200
    assert call["extra"]["user_id"] == 99
    assert call["extra"]["duration_ms"] >= 0
