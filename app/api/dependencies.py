from typing import Annotated
from fastapi import Depends
from app.services.wallets import WalletService
from app.services.operations import OperationService
from app.repository.wallet import WalletRepository
from app.repository.operation import OperationRepository
from app.core.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.pagination import Pagination

DBDep = Annotated[AsyncSession, Depends(get_db)]


async def get_wallet_repository_dep(db: DBDep) -> WalletRepository:
    return WalletRepository(db=db)


async def get_operation_repository_dep(db: DBDep) -> OperationRepository:
    return OperationRepository(db=db)


WalletRepositoryDep = Annotated[WalletRepository, Depends(get_wallet_repository_dep)]

OperationRepositoryDep = Annotated[
    OperationRepository, Depends(get_operation_repository_dep)
]


async def get_wallet_service_dep(wallet_repo: WalletRepositoryDep) -> WalletService:
    return WalletService(wallet_repo=wallet_repo)


async def get_operation_service_dep(
    operation_repo: OperationRepositoryDep,
) -> OperationService:
    return OperationService(operation_repo=operation_repo)


WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service_dep)]
OpServiceDep = Annotated[OperationService, Depends(get_operation_service_dep)]


PaginationDep = Annotated[Pagination, Depends()]
