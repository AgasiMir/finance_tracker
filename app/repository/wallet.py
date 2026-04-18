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

    async def is_wallet_exist(self, wallet_name: str, user_id: int) -> Wallet:
        return await self.db.scalar(
            select(Wallet).where(
                Wallet.name == wallet_name,
                Wallet.user_id == user_id,
            )
        )

    async def get_wallet_by_name(self, wallet_name: str, user_id: int) -> WalletPublic:
        wallet = await self.db.scalar(
            select(Wallet).where(
                Wallet.name == wallet_name,
                Wallet.user_id == user_id,
            )
        )
        return self._from_db(wallet)

    async def get_all_wallets(self, offset, limit, user_id: int) -> list[WalletPublic]:
        wallets = await self.db.scalars(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .order_by(Wallet.id)
            .offset(offset)
            .limit(limit)
        )
        return [self._from_db(obj) for obj in wallets.all()]

    async def create_wallet(self, wallet: WalletCreate, user_id: int) -> WalletPublic:
        db_wallet = Wallet(**wallet.model_dump(), user_id=user_id)
        self.db.add(db_wallet)
        await self.db.commit()
        await self.db.refresh(db_wallet)

        return self._from_db(db_wallet)
