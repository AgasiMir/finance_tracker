from typing import Annotated
from fastapi import Depends
from app.services.wallets import WalletService
from app.services.operations import OperationService
from app.repository.wallet import WalletRepository
from app.core.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession


DBDep = Annotated[AsyncSession, Depends(get_db)]


async def get_wallet_repository_dep(db: DBDep) -> WalletRepository:
    return WalletRepository(db=db)


WalletRepositoryDep = Annotated[WalletRepository, Depends(get_wallet_repository_dep)]


async def get_wallet_service_dep(wallet_repo: WalletRepositoryDep) -> WalletService:
    return WalletService(wallet_repo=wallet_repo)


WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service_dep)]


async def get_operation_service_dep(
    wallet_repo: WalletRepositoryDep,
) -> OperationService:
    return OperationService(wallet_repo=wallet_repo)


OpServiceDep = Annotated[OperationService, Depends(get_operation_service_dep)]
