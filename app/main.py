from contextlib import asynccontextmanager
from app.api.public.user import router as public_user_router
from app.api.private.user import router as private_user_router
from app.api.private.role import router as private_role_router
from app.api.private.permission import router as private_permission_router
from app.api.private.menu import router as private_menu_router
from app.db.session import init_engine, close_engine
from app.core.tracing import init_tracer
from app.core.redis import RedisClient
from app.exceptions.handlers import register_exception_handlers
from app.core.logging import init_logging, get_logger
from app.middlewares.metrics import metrics_middleware
from app.middlewares.trace import trace_middleware
from app.middlewares.logging import logging_middleware
from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response


init_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== 启动阶段 =====
    logger.info("日志初始化成功")
    await init_engine()
    logger.info("数据库初始化成功")
    await RedisClient.init()
    logger.info("redis初始化成功")

    yield

    # ===== 关闭阶段 =====
    await close_engine()
    logger.info("数据库关闭成功")
    await RedisClient.close()
    logger.info("redis关闭成功")

app = FastAPI(lifespan=lifespan)
# 初始化 OpenTelemetry
init_tracer(app)
# 注册middleware
app.middleware("http")(metrics_middleware)
app.middleware("http")(logging_middleware)
app.middleware("http")(trace_middleware)
# 注册异常处理
register_exception_handlers(app)
# 注册路由
app.include_router(public_user_router, prefix="/api")
app.include_router(private_user_router, prefix="/api")
app.include_router(private_role_router, prefix="/api")
app.include_router(private_permission_router, prefix="/api")
app.include_router(private_menu_router, prefix="/api")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
