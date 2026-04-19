from typing import Annotated
from fastapi import Depends
from app.auth import get_current_user
from app.models.user import User

from app.utils.pagination import Pagination
from app.core.database import async_session
from app.uow.uow import DBManager


async def get_db():
    async with DBManager(session_factory=async_session) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]

PaginationDep = Annotated[Pagination, Depends()]
UserDep = Annotated[User, Depends(get_current_user)]

