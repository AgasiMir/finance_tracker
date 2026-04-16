from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet
from app.schemas import WalletPublic, WalletCreate


class WalletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _from_db(model: Wallet) -> WalletPublic:
        return WalletPublic.model_validate(model)

    async def is_wallet_exist(self, wallet_name: str) -> bool: 
        return await self.db.scalar(select(Wallet).where(Wallet.name == wallet_name))

    async def get_wallet_by_name(self, wallet_name) -> WalletPublic:
        wallet = await self.db.scalar(select(Wallet).where(Wallet.name == wallet_name))
        return self._from_db(wallet)

    async def get_all_wallets(self) -> list[WalletPublic]:
        wallets = await self.db.scalars(select(Wallet))
        return [self._from_db(obj) for obj in wallets.all()]

    async def create_wallet(self, wallet: WalletCreate):
        db_wallet = Wallet(**wallet.model_dump())
        self.db.add(db_wallet)
        await self.db.commit()
        await self.db.refresh(db_wallet)

        return self._from_db(db_wallet)
