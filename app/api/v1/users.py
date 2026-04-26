from fastapi import APIRouter, Body, Depends, Request, status
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


@router.post(
    "/create-user",
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    response_model=UserPublic,
)
async def create_user(user: UserCreate, db: DBDep):
    try:
        return await UserService(db).create_user(user)
    except UserAlreadyExistsException:
        raise UserAlreadyHTTPExistsException


@router.post("/token", summary="Login")
async def login(
    db: DBDep, request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        return await UserService(db).login(
            form_data.username,
            form_data.password,
            request.client.host,
        )
    except IncorrectCredentialsException:
        raise IncorrectCredentialsHTTPException


@router.post("/refresh-token", summary="Refresh token")
async def refresh_token(db: DBDep, refresh_token: str = Body(..., embed=True)):
    """
    Обновляет access_token с помощью refresh_token.
    """
    try:
        return await UserService(db).refresh_token(refresh_token)
    except CredentialsException:
        raise CredentialsHTTPException
