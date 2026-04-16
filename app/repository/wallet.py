from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet, Operation
from app.schemas import WalletPublic, WalletCreate, OperationCreate


class WalletRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _from_db(model: Wallet) -> WalletPublic:
        return WalletPublic.model_validate(model)

    async def is_wallet_exist(self, wallet_name: str) -> bool:
        wallets = await self.db.scalars(select(Wallet.name))
        return wallet_name in wallets.all()

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

    async def add_money(self, operation: OperationCreate):
        wallet = await self.db.scalar(
            select(Wallet).where(Wallet.name == operation.wallet_name)
        )

        db_operation = Operation(**operation.model_dump(), wallet_id=wallet.id)
        self.db.add(db_operation)

        wallet.balance += operation.amount

        await self.db.commit()
        await self.db.refresh(db_operation)
        await self.db.refresh(wallet)

        return {
            "message": f"Wallet {operation.wallet_name!r} balance increased by {operation.amount}",
            "description": operation.description,
            "new_balance": wallet.balance,
        }
