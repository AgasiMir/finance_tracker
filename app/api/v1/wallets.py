from fastapi import APIRouter, Depends, status
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

from app.schemas import WalletCreate, WalletPublic
from app.api.dependencies import PaginationDep, UserDep, DBDep
from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)

from app.exceptions.fastapi_exceptions import (
    WalletNotFoundHTTPException,
    WalletAlreadyHTTPExistsException,
)
from app.services.wallets import WalletService
from app.utils.prom_metrics import REQUESTS_TOTAL

router = APIRouter(
    prefix="/api/v1/wallet",
    tags=["wallets 💰💰💰"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.SECOND * 2))))],
)


@router.get("/my-wallets", response_model=list[WalletPublic])
@cache(expire=30)
async def get_my_wallets(db: DBDep, pagination: PaginationDep, current_user: UserDep):
    page = pagination.page
    offset = (page - 1) * pagination.page_size
    limit = pagination.page_size

    REQUESTS_TOTAL.labels(method="GET", endpoint="/api/v1/wallet/my-wallets/").inc()

    return await WalletService(db).get_wallets(offset, limit, current_user.id)


@router.get("/{wallet_name}", response_model=WalletPublic)
async def get_wallet_by_name(db: DBDep, wallet_name: str, current_user: UserDep):
    try:
        return await WalletService(db).get_wallet_by_name(wallet_name, current_user.id)
    except WalletNotFoundException as err:
        raise WalletNotFoundHTTPException(err.detail)


@router.post(
    "/create-wallet",
    status_code=status.HTTP_201_CREATED,
    response_model=WalletPublic,
)
async def create_wallet(db: DBDep, wallet: WalletCreate, current_user: UserDep):
    try:
        return await WalletService(db).create_wallet(wallet, current_user.id)
    except WalletAlreadyExistsException:
        raise WalletAlreadyHTTPExistsException(wallet.name)
