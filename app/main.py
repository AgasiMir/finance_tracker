from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Response
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_client import generate_latest

from app.api.v1 import routers
from app.init import redis_manager
from app.log import log_requests


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi_cache")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan, title="Finance Tracker")

app.middleware("http")(log_requests)


@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(), media_type="text/plain; version=0.0.4; charset=utf-8"
    )


for router in routers:
    app.include_router(router)
