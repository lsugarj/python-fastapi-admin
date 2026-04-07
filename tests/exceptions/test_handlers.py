from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.exceptions.handlers import register_exception_handlers
from app.middlewares.trace import TRACE_HEADER, trace_middleware
from app.exceptions.codes import Code
from app.exceptions.business import BusinessException


def test_request_validation_error_is_wrapped():
    app = FastAPI()
    app.middleware("http")(trace_middleware)
    register_exception_handlers(app)

    @app.get("/needs-int/{x}")
    def needs_int(x: int):
        return {"x": x}

    client = TestClient(app)
    resp = client.get("/needs-int/not-an-int", headers={TRACE_HEADER: "tid-422"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == Code.VALIDATION_ERROR
    assert body["trace_id"] == "tid-422"
    assert isinstance(body["error"], list)


def test_http_exception_handler_maps_401_403_404():
    app = FastAPI()
    app.middleware("http")(trace_middleware)
    register_exception_handlers(app)

    @app.get("/unauth")
    def unauth():
        raise HTTPException(status_code=401, detail="未登录")

    @app.get("/forbidden")
    def forbidden():
        raise HTTPException(status_code=403, detail="没权限")

    client = TestClient(app)

    r1 = client.get("/unauth", headers={TRACE_HEADER: "tid-401"})
    assert r1.status_code == 401
    assert r1.json()["code"] == Code.NO_LOGIN
    assert r1.json()["message"] == "未登录"
    assert r1.json()["trace_id"] == "tid-401"

    r2 = client.get("/forbidden", headers={TRACE_HEADER: "tid-403"})
    assert r2.status_code == 403
    assert r2.json()["code"] == Code.NO_PERMISSION
    assert r2.json()["message"] == "没权限"
    assert r2.json()["trace_id"] == "tid-403"

    r3 = client.get("/not-exist", headers={TRACE_HEADER: "tid-404"})
    assert r3.status_code == 404
    assert r3.json()["code"] == Code.ROUTE_NOT_FOUND
    assert r3.json()["trace_id"] == "tid-404"


def test_business_exception_is_wrapped_into_http_200():
    app = FastAPI()
    app.middleware("http")(trace_middleware)
    register_exception_handlers(app)

    @app.get("/biz")
    def biz():
        raise BusinessException(12345, "biz error")

    client = TestClient(app)
    resp = client.get("/biz", headers={TRACE_HEADER: "tid-biz"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 12345
    assert body["message"] == "biz error"
    assert body["trace_id"] == "tid-biz"


def test_unhandled_exception_is_wrapped_into_500():
    app = FastAPI()
    app.middleware("http")(trace_middleware)
    register_exception_handlers(app)

    @app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/boom", headers={TRACE_HEADER: "tid-500"})
    assert resp.status_code == 500
    body = resp.json()
    assert body["code"] == Code.SERVER_ERROR
    assert body["trace_id"] == "tid-500"
