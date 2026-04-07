from app.core import metrics as core_metrics


def test_metrics_are_defined_with_expected_labels_and_can_be_used():
    assert core_metrics.REQUEST_COUNT._name == "http_requests"
    assert core_metrics.REQUEST_LATENCY._name == "http_request_duration_seconds"
    assert core_metrics.IN_PROGRESS._name == "http_requests_in_progress"
    assert core_metrics.EXCEPTION_COUNT._name == "http_exceptions"

    assert core_metrics.REQUEST_COUNT._labelnames == ("method", "path", "status")
    assert core_metrics.REQUEST_LATENCY._labelnames == ("method", "path")
    assert core_metrics.EXCEPTION_COUNT._labelnames == ("method", "path", "exception")

    core_metrics.REQUEST_LATENCY.labels(method="GET", path="/x").observe(0.01)
    core_metrics.REQUEST_COUNT.labels(method="GET", path="/x", status=200).inc()
    core_metrics.EXCEPTION_COUNT.labels(method="GET", path="/x", exception="ValueError").inc()
    core_metrics.IN_PROGRESS.inc()
    core_metrics.IN_PROGRESS.dec()

    request_samples = list(core_metrics.REQUEST_COUNT.collect())[0].samples
    assert any(s.name == "http_requests_total" for s in request_samples)

    exception_samples = list(core_metrics.EXCEPTION_COUNT.collect())[0].samples
    assert any(s.name == "http_exceptions_total" for s in exception_samples)
