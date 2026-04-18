from .wallets import router as wallets_router
from .operations import router as operations_router
from app.api.handlers import router as handlers_router
from .users import router as user_router


routers = [
    handlers_router,
    user_router,
    wallets_router,
    operations_router,
]
