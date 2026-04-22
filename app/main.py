from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.v1 import routers
from app.init import redis_manager
from app.middlewares.log import log_requests
from app.middlewares.cache_middleware import dispatch
from app.middlewares.metrics_middleware import metrics_middleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan, title="Finance Tracker")

app.middleware("http")(log_requests)
app.middleware("http")(dispatch)
app.middleware("http")(metrics_middleware)


# @app.get("/metrics")
# async def metrics():
#     return Response(
#         content=generate_latest(),
#         media_type="text/plain; version=0.0.4; charset=utf-8",
#     )


@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """
    Эндпоинт для сбора метрик Prometheus.
    Доступ: GET /metrics
    Content-Type: text/plain
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


for router in routers:
    app.include_router(router)
