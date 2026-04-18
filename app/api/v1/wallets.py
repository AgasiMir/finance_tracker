from fastapi import APIRouter, Depends, status
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

from app.schemas import WalletCreate, WalletPublic
from app.api.dependencies import WalletServiceDep, PaginationDep, UserDep
from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)

from app.exceptions.fastapi_exceptions import (
    WalletNotFoundHTTPException,
    WalletAlreadyHTTPExistsException,
)

router = APIRouter(
    prefix="/api/v1/wallet",
    tags=["💰💰💰"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 2))))],
)


@router.get("/my_wallets", response_model=list[WalletPublic])
@cache(expire=30)
async def get_my_wallets(
    wallet_service: WalletServiceDep,
    pagination: PaginationDep,
    current_user: UserDep,
):
    page = pagination.page
    offset = (page - 1) * pagination.page_size
    limit = pagination.page_size

    return await wallet_service.get_wallets(offset, limit, current_user.id)


@router.get("/{wallet_name}", response_model=WalletPublic)
async def get_wallet_by_name(
    wallet_service: WalletServiceDep,
    wallet_name: str,
    current_user: UserDep,
):
    try:
        return await wallet_service.get_wallet_by_name(wallet_name, current_user.id)
    except WalletNotFoundException as err:
        raise WalletNotFoundHTTPException(err.detail)
    except Exception as err:
        return {"error": str(err)}


@router.post(
    "/create_wallet",
    status_code=status.HTTP_201_CREATED,
    response_model=WalletPublic,
)
async def create_wallet(
    wallet_service: WalletServiceDep,
    wallet: WalletCreate,
    current_user: UserDep,
):
    try:
        return await wallet_service.create_wallet(wallet, current_user.id)
    except WalletAlreadyExistsException:
        raise WalletAlreadyHTTPExistsException(wallet.name)
    except Exception as err:
        return {"error": str(err)}
