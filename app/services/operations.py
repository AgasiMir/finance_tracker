from app.schemas import OperationCreate
from app.repository.operation import OperationRepository

from app.exceptions import WalletNotFoundException


class OperationService:
    def __init__(self, operation_repo: OperationRepository):
        self.operation_repo = operation_repo

    async def add_money(self, operation: OperationCreate):
        if not await self.operation_repo._get_wallet(operation.wallet_name):
            raise WalletNotFoundException

        res = await self.operation_repo.add_money(operation)
        return res

    # async def add_expense(self, operation: OperationCreate):
    #     if not await self.wallet_repo.is_wallet_exist(operation.wallet_name):
    #         raise WalletNotFoundException

    #     balance = await self.wallet_repo.get_wallet_balance_by_name(
    #         operation.wallet_name
    #     )
    #     if balance < operation.amount:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Insufficient funds. Available: {balance}",
    #         )

    #     new_balance = await self.wallet_repo.add_expence(
    #         operation.wallet_name, operation.amount
    #     )

    #     return {
    #         "message": "Expense added",
    #         "wallet": operation.wallet_name,
    #         "amount": operation.amount,
    #         "description": operation.description,
    #         "new_balance": new_balance,
    #     }
