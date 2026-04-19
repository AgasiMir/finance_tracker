from fastapi import APIRouter, Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
from fastapi_cache.decorator import cache

from app.services.operations import OperationService
from app.utils.sort_operations import Sort, Direction
from app.utils.operations_filter import Filter
from app.schemas import (
    OperationCreate,
    OperationPublic,
    OperationsHistory,
    TransferMoneyCreate,
    TransferMoneyPublic,
)
from app.api.dependencies import PaginationDep, UserDep, DBDep

from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    InsufficientFundsException,
    SameWalletException,
)
from app.exceptions.fastapi_exceptions import (
    SameWalletHTTPException,
    InsufficientFundsHTTPException,
    WalletNotFoundHTTPException,
)

router = APIRouter(
    prefix="/api/v1/operations",
    tags=["💵💶💷💴"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 2))))],
)


@router.get("/my-operations", response_model=list[OperationsHistory])
@cache(expire=30)
async def get_my_operations(
    db: DBDep,
    sort: Sort,
    dir: Direction,
    pagination: PaginationDep,
    current_user: UserDep,
    filter: Filter | None = None,
):
    page = pagination.page
    offset = (page - 1) * pagination.page_size
    limit = pagination.page_size

    filter = filter.value if filter else None

    return await OperationService(db).get_all_operations(
        sort.name, dir.name, offset, limit, current_user.id, filter
    )


@router.post("/add", response_model=OperationPublic)
async def add_money(operation: OperationCreate, db: DBDep, curretn_user: UserDep):
    try:
        return await OperationService(db).add_money(operation, curretn_user.id)
    except WalletNotFoundException as err:
        raise WalletNotFoundHTTPException(err.detail)
    except Exception as err:
        raise err


@router.post("/withdraw", response_model=OperationPublic)
async def withdraw_money(operation: OperationCreate, db: DBDep, current_user: UserDep):
    try:
        return await OperationService(db).withdraw_money(operation, current_user.id)
    except WalletNotFoundException as err:
        raise WalletNotFoundHTTPException(err.detail)
    except InsufficientFundsException as err:
        raise InsufficientFundsHTTPException(err.detail)
    except Exception as err:
        raise err


@router.post("/transfer", response_model=TransferMoneyPublic)
async def transfer_money(
    transfer: TransferMoneyCreate, db: DBDep, current_user: UserDep
):
    try:
        return await OperationService(db).transfer_money(transfer, current_user.id)
    except WalletNotFoundException as err:
        raise WalletNotFoundHTTPException(err.detail)
    except InsufficientFundsException as err:
        raise InsufficientFundsHTTPException(err.detail)
    except SameWalletException:
        raise SameWalletHTTPException
    except Exception as err:
        raise err
