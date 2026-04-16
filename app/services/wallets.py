from fastapi import HTTPException, status

from app.schemas import WalletCreate
from app.repository.wallet import WalletRepository


class WalletService:
    def __init__(self, wallet_repo: WalletRepository):
        self.wallet_repo = wallet_repo

    async def get_wallets(self):
        return await self.wallet_repo.get_all_wallets()

    async def get_wallet_by_name(self, wallet_name: str):
        if not await self.wallet_repo.is_wallet_exist(wallet_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet {wallet_name!r} not found",
            )
        return await self.wallet_repo.get_wallet_by_name(wallet_name)

    async def create_wallet(self, wallet: WalletCreate):
        if await self.wallet_repo.is_wallet_exist(wallet.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Wallet {wallet.name!r} already exists",
            )

        return await self.wallet_repo.create_wallet(wallet)
