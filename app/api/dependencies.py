from typing import Annotated
from fastapi import Depends
import jwt

from app.models.user import User

from app.utils.pagination import Pagination
from app.core.database import async_session
from app.uow.uow import DBManager

from app.config import settings

from fastapi.security import OAuth2PasswordBearer
from app.exceptions.fastapi_exceptions import (
    CredentialsHTTPException,
    JWTExpiredSignatureException,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


async def get_db():
    async with DBManager(session_factory=async_session) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]

PaginationDep = Annotated[Pagination, Depends()]


async def get_current_user(db: DBDep, token: str = Depends(oauth2_scheme)):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if email is None or token_type != "access":
            raise CredentialsHTTPException
    except jwt.ExpiredSignatureError:
        raise JWTExpiredSignatureException

    except jwt.PyJWTError:
        raise CredentialsHTTPException

    user = await db.users.get_user_by_email(email)

    if user is None:
        raise CredentialsHTTPException
    return user


UserDep = Annotated[User, Depends(get_current_user)]
