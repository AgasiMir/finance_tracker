from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet, Operation
from app.schemas import OperationCreate, OperationsHistory


class OperationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _from_db(model: Operation) -> OperationsHistory:
        return OperationsHistory.model_validate(model)

    async def _get_wallet(self, wallet_name: str):
        return await self.db.scalar(select(Wallet).where(Wallet.name == wallet_name))

    async def get_all_operations(self):
        operations = await self.db.scalars(select(Operation))
        return [self._from_db(obj) for obj in operations.all()]

    async def add_money(self, operation: OperationCreate):
        wallet = await self._get_wallet(operation.wallet_name)

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

    async def withdraw_money(self, operation: OperationCreate):
        wallet = await self._get_wallet(operation.wallet_name)

        db_operation = Operation(**operation.model_dump(), wallet_id=wallet.id)
        self.db.add(db_operation)

        wallet.balance -= operation.amount

        await self.db.commit()
        await self.db.refresh(db_operation)
        await self.db.refresh(wallet)

        return {
            "message": f"Wallet {operation.wallet_name!r} balance decreased by {operation.amount}",
            "description": operation.description,
            "new_balance": wallet.balance,
        }
