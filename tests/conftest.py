# ruff: noqa: E402, F401, F403

import pytest
from typing import AsyncGenerator
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

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


@pytest.fixture
async def db():
    async for db in get_db_null_pull():
        yield db


app.dependency_overrides[get_db] = get_db_null_pull


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
