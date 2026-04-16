from fastapi import APIRouter, Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

from app.schemas import OperationCreate, OperationPublic
from app.api.dependencies import OpServiceDep

from app.exceptions import (
    WalletNotFoundException,
    WalletNotFoundHTTPException,
    InsufficientFundsException,
    InsufficientFundsHTTPException,
)

router = APIRouter(
    prefix="/api/v1/operations",
    tags=["💵💶💷💴"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 2))))],
)


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
    except InsufficientFundsException as err:
        raise InsufficientFundsHTTPException(err.detail)
    except Exception as err:
        raise err
