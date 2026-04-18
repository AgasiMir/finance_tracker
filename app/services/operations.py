from app.schemas import OperationCreate, TransferMoneyCreate, OperationsHistory
from app.repository.operation import OperationRepository

from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    InsufficientFundsException,
    SameWalletException,
)


class OperationService:
    def __init__(self, operation_repo: OperationRepository):
        self.operation_repo = operation_repo

    async def get_all_operations(
        self,
        sort_param: str,
        dir: str,
        offset: int,
        limit: int,
        user_id: int,
        filter: str | None = None,
    ) -> list[OperationsHistory]:
        return await self.operation_repo.get_all_operations(
            sort_param,
            dir,
            offset,
            limit,
            user_id,
            filter,
        )

    async def add_money(self, operation: OperationCreate, user_id: int) -> dict:
        if not await self.operation_repo._get_wallet(operation.wallet_name, user_id):
            raise WalletNotFoundException(operation.wallet_name)

        res = await self.operation_repo.add_money(operation, user_id)
        return res

    async def withdraw_money(self, operation: OperationCreate, user_id: int) -> dict:
        wallet = await self.operation_repo._get_wallet(operation.wallet_name, user_id)
        if not wallet:
            raise WalletNotFoundException(operation.wallet_name)

        if wallet.balance < operation.amount:
            raise InsufficientFundsException(wallet.name, wallet.balance)

        res = await self.operation_repo.withdraw_money(operation, user_id)
        return res

    async def transfer_money(self, transfer: TransferMoneyCreate, user_id: int) -> dict:
        wallet_from = await self.operation_repo._get_wallet(
            transfer.wallet_from,
            user_id,
        )
        if not wallet_from:
            raise WalletNotFoundException(transfer.wallet_from)

        wallet_to = await self.operation_repo._get_wallet(transfer.wallet_to, user_id)
        if not wallet_to:
            raise WalletNotFoundException(transfer.wallet_to)

        if wallet_from.name == wallet_to.name:
            raise SameWalletException

        if wallet_from.balance < transfer.amount:
            raise InsufficientFundsException(
                transfer.wallet_from,
                wallet_from.balance,
            )

        res = await self.operation_repo.transfer_money(transfer, user_id)
        return res
