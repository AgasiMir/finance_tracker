# ruff: noqa: E402, F401

import pytest
from typing import AsyncGenerator
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

from httpx import ASGITransport, AsyncClient

from app.main import app
from app.config import settings
from app.core.db_depends import get_db


@pytest.fixture(autouse=True, scope="session")
def check_test_mode():
    assert settings.ENVIRONMENT == "TEST"


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
