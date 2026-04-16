from fastapi import FastAPI
from app.api.v1 import routers
from app.log import log_requests


app = FastAPI(title="Finance Tracker")

app.middleware("http")(log_requests)


for router in routers:
    app.include_router(router)
