from app.schemas import OperationCreate, TransferMoneyCreate, OperationsHistory
from app.uow.uow import DBManager


class OperationService:
    def __init__(self, operation_repo: DBManager):
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
        return await self.operation_repo.operations.get_all_operations(
            sort_param,
            dir,
            offset,
            limit,
            user_id,
            filter,
        )

    async def add_money(self, operation: OperationCreate, user_id: int) -> dict:

        return await self.operation_repo.operations.add_money(operation, user_id)

    async def withdraw_money(self, operation: OperationCreate, user_id: int) -> dict:

        return await self.operation_repo.operations.withdraw_money(operation, user_id)

    async def transfer_money(self, transfer: TransferMoneyCreate, user_id: int) -> dict:

        return await self.operation_repo.operations.transfer_money(transfer, user_id)
