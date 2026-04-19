# ruff: noqa: E402, F401, F403

import pytest
from typing import AsyncGenerator
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()
# mock.patch("fastapi_limiter.depends.RateLimiter", lambda *args, **kwargs: lambda f: f).start()

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.config import settings
from app.core.db_depends import get_db
from app.core.database import Base, engine_null_pull, async_session_null_pool
from app.models import *
from app.uow.uow import DBManager


@pytest.fixture(autouse=True, scope="session")
def check_test_mode():
    assert settings.ENVIRONMENT == "TEST"


async def get_db_null_pull():
    async with DBManager(session_factory=async_session_null_pool) as db:
        yield db


app.dependency_overrides[get_db] = get_db_null_pull


@pytest.fixture
async def db():
    async for db in get_db_null_pull():
        yield db


@pytest.fixture(autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pull.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# @pytest.fixture(scope="session")
# async def register_user(async_client):
#     response = await async_client.post(
#         "/users/create_user",
#         json={"email": "test@example.com", "password": "12345678"},
#     )
#     assert response.status_code == 200, f"Failed to create user: {response.text}"


# @pytest.fixture(scope="session")
# async def authenticated_ac(register_user):
#     # Создаем новый клиент для авторизованных запросов
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test",
#     ) as ac:
#         # Регистрация уже выполнена через register_user
#         response = await ac.post(
#             "/users/token",
#             data={"username": "test@example.com", "password": "12345678"},
#         )
#         assert response.status_code == 200, f"Failed to get token: {response.text}"
#         token = response.json().get("access_token")
#         print(token)
#         assert token is not None, "Token is missing in response"
#         ac.headers["Authorization"] = f"Bearer {token}"
#         yield ac
