from prometheus_client import Counter, Histogram, Gauge

# =========================
# 指标定义（全局单例）
# =========================

# 请求总数
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

# 请求耗时（秒）
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1,
             0.25, 0.5, 1, 2, 5)
)

# 当前请求数
IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "In progress requests"
)

# 异常计数
EXCEPTION_COUNT = Counter(
    "http_exceptions_total",
    "Total exceptions",
    ["method", "path", "exception"],
)