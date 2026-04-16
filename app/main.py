from fastapi import FastAPI
from app.api.v1 import routers


app = FastAPI(title="Finance Tracker")


for router in routers:
    app.include_router(router)
