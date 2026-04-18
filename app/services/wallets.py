from app.schemas import WalletCreate, WalletPublic
from app.repository.wallet import WalletRepository

from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)


class WalletService:
    def __init__(self, wallet_repo: WalletRepository):
        self.wallet_repo = wallet_repo

    async def get_wallets(self, offset, limit, user_id: int) -> list[WalletPublic]:
        return await self.wallet_repo.get_all_wallets(offset, limit, user_id)

    async def get_wallet_by_name(self, wallet_name: str, user_id: int) -> WalletPublic:
        if not await self.wallet_repo.is_wallet_exist(wallet_name, user_id):
            raise WalletNotFoundException(wallet_name)

        return await self.wallet_repo.get_wallet_by_name(wallet_name, user_id)

    async def create_wallet(self, wallet: WalletCreate, user_id: int) -> WalletPublic:
        if await self.wallet_repo.is_wallet_exist(wallet.name, user_id):
            raise WalletAlreadyExistsException

        return await self.wallet_repo.create_wallet(wallet, user_id)
