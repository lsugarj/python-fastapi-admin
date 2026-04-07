from fastapi import Request
from app.core.context import set_trace_id
from opentelemetry import trace

TRACE_HEADER = "X-Trace-Id"


async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get(TRACE_HEADER)
    if not trace_id:
        current_span = trace.get_current_span()
        ctx = current_span.get_span_context()
        if ctx.is_valid:
            trace_id = format(ctx.trace_id, '032x')
        else:
            # 方案A：生成一个随机的 trace_id（用于调试）
            import uuid
            trace_id = uuid.uuid4().hex
    trace_id = set_trace_id(trace_id)

    # 放到 request.state（保险）
    request.state.trace_id = trace_id

    response = await call_next(request)
    response.headers[TRACE_HEADER] = trace_id

    return response