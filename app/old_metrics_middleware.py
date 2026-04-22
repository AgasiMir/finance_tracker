import time
from fastapi import Request

from app.utils.prom_metrics import REQUESTS_TOTAL, REQUEST_DURATION


async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
    ).observe(duration)

    REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=str(response.status_code),
    ).inc()

    return response
