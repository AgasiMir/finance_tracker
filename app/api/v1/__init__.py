from .wallets import router as wallets_router
from .operations import router as operations_router
from app.api.handlers import router as handlers_router


routers = [handlers_router, wallets_router, operations_router]
