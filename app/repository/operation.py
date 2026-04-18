from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet, Operation
from app.schemas import OperationCreate, OperationsHistory, TransferMoneyCreate


class OperationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _from_db(model: Operation) -> OperationsHistory:
        return OperationsHistory.model_validate(model)

    async def _get_wallet(self, wallet_name: str, user_id) -> Wallet:
        return await self.db.scalar(
            select(Wallet).where(
                Wallet.name == wallet_name,
                Wallet.user_id == user_id,
            )
        )

    async def get_all_operations(
        self,
        sort_param: str,
        dir: str,
        offset: int,
        limit: int,
        user_id: int,
        filter: str | None = None,
    ) -> list[OperationsHistory]:
        filters = []

        if filter:
            filters.append(Operation.type == filter)

        if dir == "asc":
            operations = await self.db.scalars(
                select(Operation)
                .join(Wallet, Operation.wallet_id == Wallet.id)
                .where(*filters, Wallet.user_id == user_id)
                .order_by(eval(f"Operation.{sort_param}"))
                .limit(limit)
                .offset(offset)
            )
        elif dir == "desc":
            operations = await self.db.scalars(
                select(Operation)
                .join(Operation.wallet)
                .where(*filters, Wallet.user_id == user_id)
                .order_by(desc(eval(f"Operation.{sort_param}")))
                .limit(limit)
                .offset(offset)
            )
        return [self._from_db(obj) for obj in operations.all()]

    async def add_money(self, operation: OperationCreate, user_id: int) -> dict:
        wallet = await self._get_wallet(operation.wallet_name, user_id)

        db_operation = Operation(
            **operation.model_dump(), wallet_id=wallet.id, type="income"
        )
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

    async def withdraw_money(self, operation: OperationCreate, user_id: int) -> dict:
        wallet = await self._get_wallet(operation.wallet_name, user_id)

        db_operation = Operation(
            **operation.model_dump(), wallet_id=wallet.id, type="expense"
        )
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

    async def transfer_money(self, transfer: TransferMoneyCreate, user_id: int) -> dict:
        wallet_from = await self._get_wallet(transfer.wallet_from, user_id)
        wallet_to = await self._get_wallet(transfer.wallet_to, user_id)

        wallet_from.balance -= transfer.amount
        wallet_to.balance += transfer.amount

        await self.db.commit()

        return {
            "add": f"Wallet {transfer.wallet_to!r} + {transfer.amount} = {wallet_to.balance}",
            "withdraw": f"Wallet {transfer.wallet_from!r} - {transfer.amount} = {wallet_from.balance}",
        }
