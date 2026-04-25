from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter


from app.email import send_email
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
async def create_user(user: UserCreate, db: DBDep, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(
            send_email,
            user.email,
            "Регистрация на сайте",
            body=f"{user.email}! Добро пожаловать",
        )
        return await UserService(db).create_user(user)
    except UserAlreadyExistsException:
        raise UserAlreadyHTTPExistsException


@router.post("/token", summary="Login")
async def login(
    db: DBDep,
    background_tasks: BackgroundTasks,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    try:
        timezone_offset = +3.0
        tzinfo = timezone(timedelta(hours=timezone_offset))
        current_datetime = datetime.now(tzinfo)
        current_datetime = datetime.strftime(current_datetime, "%Y-%m-%d %H:%M:%S")
        background_tasks.add_task(
            send_email,
            form_data.username,
            "Вход в систему",
            body=f"{form_data.username} Был осуществлен вход в систему c IP {request.client.host} в {current_datetime}",
        )
        return await UserService(db).login(form_data.username, form_data.password)
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
