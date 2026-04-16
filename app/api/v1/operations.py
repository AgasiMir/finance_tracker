from fastapi import APIRouter
from app.schemas import OperationCreate, OperationPublic
from app.api.dependencies import OpServiceDep

from app.exceptions import (
    WalletNotFoundException,
    WalletNotFoundHTTPException,
    InsufficientFundsException,
    InsufficientFundsHTTPException,
)

router = APIRouter(prefix="/api/v1/operations", tags=["💵💶💷💴"])


@router.post("/add", response_model=OperationPublic)
async def add_money(operation: OperationCreate, op_service: OpServiceDep):
    try:
        return await op_service.add_money(operation)
    except WalletNotFoundException:
        raise WalletNotFoundHTTPException(operation.wallet_name)
    except Exception as err:
        raise err


@router.post("/withdraw", response_model=OperationPublic)
async def withdraw_money(operation: OperationCreate, op_service: OpServiceDep):
    try:
        return await op_service.withdraw_money(operation)
    except WalletNotFoundException:
        raise WalletNotFoundHTTPException(operation.wallet_name)
    except InsufficientFundsException:
        raise InsufficientFundsHTTPException
    except Exception as err:
        raise err
