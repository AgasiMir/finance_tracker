import pytest
from app.auth import hash_password
from app.schemas import UserCreate
from app.models import User
from app.exceptions.python_exceptions import (
    UserAlreadyExistsException,
)
from app.uow.uow import DBManager


@pytest.fixture()
async def get_user(db: DBManager):

    db_user = User(email="user@example.com", hashed_password=hash_password("1234abcd"))
    db.add(db_user)
    await db.flush()
    await db.commit()

    return db_user


async def test_get_user_by_email(db: DBManager, get_user):
    user = get_user

    res = await db.users.get_user_by_email(user.email)
    assert res.email == "user@example.com"


async def test_create_user(db: DBManager):
    user = UserCreate(email="user@example.com", password="1234abcd")
    res = await db.users.create_user(user)
    assert res.email == "user@example.com"


async def test_create_user_with_the_same_email(db: DBManager, get_user):
    user = UserCreate(email="user@example.com", password="1234abcd")

    with pytest.raises(UserAlreadyExistsException):
        await db.users.create_user(user)


async def test_login_user(db: DBManager, get_user):
    user = get_user
    res = await db.users.login_user(user.email, "1234abcd")
    assert isinstance(res, dict)
    assert res.get("token_type") == "bearer"


async def test_refresh_token(db: DBManager, get_user):
    user = get_user
    res = await db.users.refresh_token(user.email)
    assert isinstance(res, dict)
    assert res.get("token_type") == "bearer"
