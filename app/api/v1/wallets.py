from fastapi import APIRouter, Depends, status
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

from app.schemas import WalletCreate, WalletPublic
from app.api.dependencies import WalletServiceDep
from app.exceptions import (
    WalletNotFoundException,
    WalletAlreadyExists,
    WalletNotFoundHTTPException,
    WalletAlreadyHTTPExists,
)

router = APIRouter(
    prefix="/api/v1/wallet",
    tags=["💰💰💰"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 2))))],
)


@router.get("", response_model=list[WalletPublic])
async def get_wallets(wallet_service: WalletServiceDep):
    return await wallet_service.get_wallets()


@router.get("/{wallet_name}", response_model=WalletPublic)
async def get_wallet_by_name(wallet_service: WalletServiceDep, wallet_name: str):
    try:
        return await wallet_service.get_wallet_by_name(wallet_name)
    except WalletNotFoundException:
        raise WalletNotFoundHTTPException(wallet_name)
    except Exception as e:
        return {"error": str(e)}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WalletPublic)
async def create_wallet(wallet_service: WalletServiceDep, wallet: WalletCreate):
    try:
        return await wallet_service.create_wallet(wallet)
    except WalletAlreadyExists:
        raise WalletAlreadyHTTPExists(wallet.name)
    except Exception as e:
        return {"error": str(e)}
