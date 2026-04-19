import pytest
from app.schemas import WalletCreate, WalletPublic
from app.models import User
from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)
from app.uow.uow import DBManager


@pytest.fixture()
async def user_and_wallets(db: DBManager):
    data_1 = {
        "name": "rub",
        "description": "main_wallet",
    }

    data_2 = {"name": "usd"}

    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    wallet_1 = WalletCreate(**data_1)
    wallet_2 = WalletCreate(**data_2)

    return db_user, wallet_1, wallet_2


async def test_wallet_create(db: DBManager, user_and_wallets):
    user, wallet_1, wallet_2 = user_and_wallets

    await db.wallets.create_wallet(wallet_1, user_id=user.id)
    await db.wallets.create_wallet(wallet_2, user_id=user.id)

    res = await db.wallets.get_wallet_by_name(
        wallet_1.name,
        user_id=user.id,
    )
    assert isinstance(res, WalletPublic)


async def test_get_all_wallets(db: DBManager, user_and_wallets):
    user, wallet_1, wallet_2 = user_and_wallets

    await db.wallets.create_wallet(wallet_1, user_id=user.id)
    await db.wallets.create_wallet(wallet_2, user_id=user.id)

    res = await db.wallets.get_all_wallets(0, 10, user.id)
    assert len(res) == 2
    assert isinstance(res[1], WalletPublic)


async def test_is_wallet_exist(db: DBManager, user_and_wallets):
    user, wallet_1, wallet_2 = user_and_wallets

    await db.wallets.create_wallet(wallet_1, user_id=user.id)
    await db.wallets.create_wallet(wallet_2, user_id=user.id)

    res = await db.wallets.is_wallet_exist(wallet_1.name, user.id)
    assert res.id == 1


async def test_get_not_existing_wallet_by_name(db: DBManager):
    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    with pytest.raises(WalletNotFoundException):
        await db.wallets.get_wallet_by_name("not_existing_wallet", db_user.id)


async def test_create_wallet_with_the_same_name(db: DBManager, user_and_wallets):
    user, wallet_1, _ = user_and_wallets

    data_2 = {"name": "rub"}

    wallet_2 = WalletCreate(**data_2)

    await db.wallets.create_wallet(wallet_1, user_id=user.id)

    with pytest.raises(WalletAlreadyExistsException):
        await db.wallets.create_wallet(wallet_2, user_id=user.id)
