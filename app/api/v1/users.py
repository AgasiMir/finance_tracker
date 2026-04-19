from fastapi import APIRouter, Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter


from app.schemas import UserCreate, UserPublic
from app.api.dependencies import DBDep
from app.exceptions.python_exceptions import (
    UserAlreadyExistsException,
    IncorrectCredentialsException,
    CredentialsException,
)
from app.exceptions.fastapi_exceptions import (
    UserAlreadyHTTPExistsException,
    IncorrectCredentialsHTTPException,
    CredentialsHTTPException,
)

from fastapi.security import OAuth2PasswordRequestForm
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users 👨🏻👱🏻‍♀️🧒🏻"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 2))))],
)


@router.post("/create_user", response_model=UserPublic)
async def create_user(user: UserCreate, db: DBDep):
    try:
        return await UserService(db).create_user(user)
    except UserAlreadyExistsException:
        raise UserAlreadyHTTPExistsException
    except Exception as err:
        raise err


@router.post("/token")
async def login(db: DBDep, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return await UserService(db).login(form_data.username, form_data.password)
    except IncorrectCredentialsException:
        raise IncorrectCredentialsHTTPException
    except Exception as err:
        raise err


@router.post("/refresh-token")
async def refresh_token(refresh_token: str, db: DBDep):
    """
    Обновляет access_token с помощью refresh_token.
    """

    try:
        return await UserService(db).refresh_token(refresh_token)
    except CredentialsException:
        raise CredentialsHTTPException
    except Exception as err:
        raise err
