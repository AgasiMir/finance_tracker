from fastapi import HTTPException, status

from app.schemas import OperationRequestCreate
from app.repository.wallet import WalletRepository


class OperationService:
    def __init__(self, wallet_repo: WalletRepository):
        self.wallet_repo = wallet_repo

    async def add_income(self, operation: OperationRequestCreate):
        if not await self.wallet_repo.is_wallet_exist(operation.wallet_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet {operation.wallet_name!r} not found",
            )

        new_balance = await self.wallet_repo.add_income(
            operation.wallet_name, operation.amount
        )

        return {
            "message": "Income added",
            "wallet": operation.wallet_name,
            "amount": operation.amount,
            "description": operation.description,
            "new_balance": new_balance,
        }

    async def add_expense(self, operation: OperationRequestCreate):
        if not await self.wallet_repo.is_wallet_exist(operation.wallet_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet {operation.wallet_name!r} not found",
            )

        balance = await self.wallet_repo.get_wallet_balance_by_name(
            operation.wallet_name
        )
        if balance < operation.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds. Available: {balance}",
            )

        new_balance = await self.wallet_repo.add_expence(
            operation.wallet_name, operation.amount
        )

        return {
            "message": "Expense added",
            "wallet": operation.wallet_name,
            "amount": operation.amount,
            "description": operation.description,
            "new_balance": new_balance,
        }
