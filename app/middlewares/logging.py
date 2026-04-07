import time
from fastapi import Request
from app.core.logging import get_logger

logger = get_logger("access")


async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    cost = round((time.time() - start) * 1000, 2)

    logger.info(
        "access_log",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": cost,
            "client_ip": request.client.host if request.client else None,
            "user_id": getattr(request.state, "user_id", None)
        }
    )

    return response