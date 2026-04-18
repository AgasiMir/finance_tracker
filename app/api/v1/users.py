from fastapi import APIRouter, Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter


from app.schemas import UserCreate, UserPublic
from app.api.dependencies import UserServiceDep
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


router = APIRouter(
    prefix="/users",
    tags=["users 👨🏻👱🏻‍♀️🧒🏻"],
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(2, Duration.SECOND * 2))))],
)


@router.post("/create_user", response_model=UserPublic)
async def create_user(user: UserCreate, user_service: UserServiceDep):
    try:
        return await user_service.create_user(user)
    except UserAlreadyExistsException:
        raise UserAlreadyHTTPExistsException
    except Exception as err:
        raise err


@router.post("/token")
async def login(
    user_service: UserServiceDep, form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        return await user_service.login(form_data.username, form_data.password)
    except IncorrectCredentialsException:
        raise IncorrectCredentialsHTTPException
    except Exception as err:
        raise err


@router.post("/refresh-token")
async def refresh_token(refresh_token: str, user_service: UserServiceDep):
    """
    Обновляет access_token с помощью refresh_token.
    """

    try:
        return await user_service.refresh_token(refresh_token)
    except CredentialsException:
        raise CredentialsHTTPException
    except Exception as err:
        raise err
