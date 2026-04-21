from prometheus_client import Counter


REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint"]
)
