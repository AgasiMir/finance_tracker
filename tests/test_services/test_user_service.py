import pytest
from app.schemas import UserPublic, UserCreate
from app.models import User
from app.services.users import UserService
from app.exceptions.python_exceptions import (
    CredentialsException,
    UserAlreadyExistsException,
    IncorrectCredentialsException,
)
from app.uow.uow import DBManager
from app.auth import hash_password


@pytest.fixture
async def get_user(db: DBManager):
    db_user = User(email="user@example.com", hashed_password=hash_password("1234abcd"))
    db.add(db_user)
    await db.flush()

    return db_user


async def test_user_service_create_user(db: DBManager):
    user = UserCreate(email="user@example.com", password="1234abcd")
    user_service = UserService(db)
    res = await user_service.create_user(user)
    assert isinstance(res, UserPublic)


async def test_user_service_login_user(db: DBManager, get_user):
    user = get_user

    user_service = UserService(db)
    res = await user_service.login(user.email, "1234abcd")
    assert isinstance(res, dict)


async def test_user_service_login_user_with_incrorrect_credentials(
    db: DBManager, get_user
):
    user = get_user
    user_service = UserService(db)

    with pytest.raises(IncorrectCredentialsException):
        await user_service.login(user.email, "1234abcd_")


async def test_create_user_with_the_same_email(db: DBManager, get_user):
    user = UserCreate(email="user@example.com", password="1234abcd")
    user_service = UserService(db)

    with pytest.raises(UserAlreadyExistsException):
        await user_service.create_user(user)


async def test_service_refresh_token(db: DBManager, get_user):
    user = get_user
    user_service = UserService(db)
    data = await user_service.login(user.email, "1234abcd")

    res = await user_service.refresh_token(data["refresh_token"])
    assert isinstance(res, dict)


async def test_service_refresh_token_with_wrong_refresh_token(db: DBManager, get_user):
    user = get_user
    user_service = UserService(db)
    data = await user_service.login(user.email, "1234abcd")

    with pytest.raises(CredentialsException):
        await user_service.refresh_token(data["refresh_token"] + "abc")
