from fastapi import APIRouter, status
from app.schemas import WalletCreate, WalletPublic
from app.api.dependencies import WalletServiceDep

router = APIRouter(prefix="/api/v1/wallet", tags=["💰💰💰"])


@router.get("", response_model=list[WalletPublic])
async def get_wallets(wallet_service: WalletServiceDep):
    return await wallet_service.get_wallets()


@router.get("/{wallet_name}", response_model=WalletPublic)
async def get_wallet_by_name(wallet_service: WalletServiceDep, wallet_name: str):
    return await wallet_service.get_wallet_by_name(wallet_name)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WalletPublic)
async def create_wallet(wallet_service: WalletServiceDep, wallet: WalletCreate):
    return await wallet_service.create_wallet(wallet)
