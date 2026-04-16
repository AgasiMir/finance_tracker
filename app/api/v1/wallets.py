from fastapi import APIRouter, HTTPException, status
from app.schemas import WalletCreate, WalletPublic
from app.api.dependencies import WalletServiceDep
from app.exceptions import WalletNotFoundException, WalletAlreadyExists

router = APIRouter(prefix="/api/v1/wallet", tags=["💰💰💰"])


@router.get("", response_model=list[WalletPublic])
async def get_wallets(wallet_service: WalletServiceDep):
    return await wallet_service.get_wallets()


@router.get("/{wallet_name}", response_model=WalletPublic)
async def get_wallet_by_name(wallet_service: WalletServiceDep, wallet_name: str):
    try:
        return await wallet_service.get_wallet_by_name(wallet_name)
    except WalletNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_name!r} not found",
        )
    except Exception as e:
        return {"error": str(e)}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WalletPublic)
async def create_wallet(wallet_service: WalletServiceDep, wallet: WalletCreate):
    try:
        return await wallet_service.create_wallet(wallet)
    except WalletAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Wallet {wallet.name!r} already exists",
        )
    except Exception as e:
        return {"error": str(e)}
