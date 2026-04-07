from contextvars import ContextVar
import uuid

_trace_id: ContextVar[str] = ContextVar("trace_id", default="-")
_span_id: ContextVar[str] = ContextVar("span_id", default="-")


def set_trace_id(trace_id: str = None):
    trace_id = trace_id or str(uuid.uuid4())
    _trace_id.set(trace_id)
    return trace_id


def get_trace_id():
    return _trace_id.get()


def set_span_id(span_id: str = None):
    span_id = span_id or str(uuid.uuid4())[:8]
    _span_id.set(span_id)
    return span_id


def get_span_id():
    return _span_id.get()