import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import WalletCreate, WalletPublic
from app.models import User
from app.services.wallets import WalletService
from app.exceptions.python_exceptions import WalletNotFoundException
from app.uow.uow import DBManager


@pytest.fixture
async def user(db: DBManager):
    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    return db_user


async def test_get_wallet_by_name(db: DBManager):
    service = WalletService(db)
    with pytest.raises(WalletNotFoundException):
        await service.get_wallet_by_name("rub", 1)


async def test_get_wallets(db: AsyncSession):
    res = await WalletService(db).get_wallets(0, 10, 1)
    assert res == []


async def test_create_wallet(db: DBManager, user):
    user = user
    wallet = WalletCreate(name="rub")
    res = await WalletService(db).create_wallet(wallet, user_id=user.id)
    assert isinstance(res, WalletPublic)
