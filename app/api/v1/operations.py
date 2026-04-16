from fastapi import APIRouter
from app.schemas import OperationCreate, OperationPublic
from app.api.dependencies import OpServiceDep

from app.exceptions import WalletNotFoundException, WalletNotFoundHTTPException

router = APIRouter(prefix="/api/v1/operations", tags=["💵💶💷💴"])


@router.post("/add", response_model=OperationPublic)
async def add_income(operation: OperationCreate, op_service: OpServiceDep):
    try:
        return await op_service.add_money(operation)
    except WalletNotFoundException:
        raise WalletNotFoundHTTPException(operation.wallet_name)


@router.post("/withdraw")
async def add_expense(operation: OperationCreate, op_service: OpServiceDep):
    return await op_service.add_expense(operation)
