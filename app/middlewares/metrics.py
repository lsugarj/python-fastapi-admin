import time
from fastapi import Request
from app.core.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    IN_PROGRESS,
    EXCEPTION_COUNT,
)

async def metrics_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path

    IN_PROGRESS.inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = response.status_code

        REQUEST_COUNT.labels(
            method=method,
            path=path,
            status=status_code
        ).inc()

        return response

    except Exception as e:
        EXCEPTION_COUNT.labels(
            method=method,
            path=path,
            exception=type(e).__name__,
        ).inc()
        raise

    finally:
        duration = time.time() - start_time

        REQUEST_LATENCY.labels(
            method=method,
            path=path
        ).observe(duration)

        IN_PROGRESS.dec()