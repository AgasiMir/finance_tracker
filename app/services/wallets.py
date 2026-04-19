from app.schemas import WalletCreate, WalletPublic
from app.uow.uow import DBManager


class WalletService:
    def __init__(self, wallet_repo: DBManager):
        self.wallet_repo = wallet_repo

    async def get_wallets(self, offset, limit, user_id: int) -> list[WalletPublic]:
        return await self.wallet_repo.wallets.get_all_wallets(offset, limit, user_id)

    async def get_wallet_by_name(self, wallet_name: str, user_id: int) -> WalletPublic:

        return await self.wallet_repo.wallets.get_wallet_by_name(wallet_name, user_id)

    async def create_wallet(self, wallet: WalletCreate, user_id: int) -> WalletPublic:

        return await self.wallet_repo.wallets.create_wallet(wallet, user_id)
