from fastapi import APIRouter
from app.schemas import OperationRequestCreate, WalletPublic
from app.api.dependencies import OpServiceDep

router = APIRouter(prefix="/api/v1/operations", tags=["💵💶💷💴"])


@router.post("/income", response_model=WalletPublic)
async def add_income(operation: OperationRequestCreate, op_service: OpServiceDep):
    return await op_service.add_income(operation)


@router.post("/expense", response_model=WalletPublic)
async def add_expense(operation: OperationRequestCreate, op_service: OpServiceDep):
    return await op_service.add_expense(operation)
