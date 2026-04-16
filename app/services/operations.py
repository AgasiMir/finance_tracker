from app.schemas import OperationCreate
from app.repository.operation import OperationRepository

from app.exceptions import WalletNotFoundException, InsufficientFundsException


class OperationService:
    def __init__(self, operation_repo: OperationRepository):
        self.operation_repo = operation_repo

    async def get_all_operations(self, sort_value: str, dir: str):
        return await self.operation_repo.get_all_operations(sort_value, dir)

    async def add_money(self, operation: OperationCreate):
        if not await self.operation_repo._get_wallet(operation.wallet_name):
            raise WalletNotFoundException

        res = await self.operation_repo.add_money(operation)
        return res

    async def withdraw_money(self, operation: OperationCreate):
        wallet = await self.operation_repo._get_wallet(operation.wallet_name)
        if not wallet:
            raise WalletNotFoundException

        if wallet.balance < operation.amount:
            raise InsufficientFundsException(wallet.name, wallet.balance)

        res = await self.operation_repo.withdraw_money(operation)
        return res
