from app.schemas import WalletCreate
from app.repository.wallet import WalletRepository

from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)


class WalletService:
    def __init__(self, wallet_repo: WalletRepository):
        self.wallet_repo = wallet_repo

    async def get_wallets(self, offset, limit):
        return await self.wallet_repo.get_all_wallets(offset, limit)

    async def get_wallet_by_name(self, wallet_name: str):
        if not await self.wallet_repo.is_wallet_exist(wallet_name):
            raise WalletNotFoundException(wallet_name)

        return await self.wallet_repo.get_wallet_by_name(wallet_name)

    async def create_wallet(self, wallet: WalletCreate):
        if await self.wallet_repo.is_wallet_exist(wallet.name):
            raise WalletAlreadyExistsException

        return await self.wallet_repo.create_wallet(wallet)
