from prometheus_client import Counter, Gauge, Histogram


REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections", "Current number of active connections", ["app"]
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.3, 0.5, 1.0, 2.0, 5.0],
)
