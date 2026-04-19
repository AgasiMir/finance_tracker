import pytest
from app.schemas import (
    OperationCreate,
    TransferMoneyCreate,
    WalletCreate,
    OperationsHistory,
)
from app.models import User
from app.services.operations import OperationService
from app.uow.uow import DBManager


@pytest.fixture
async def user_wallets_operations(db: DBManager):
    wallet_data_1 = {
        "name": "rub",
        "description": "main_wallet",
    }

    wallet_data_2 = {"name": "usd"}

    operation_data_1 = {
        "wallet_name": "rub",
        "amount": 100.0,
        "description": "bonus",
    }

    operation_data_2 = {
        "wallet_name": "usd",
        "amount": 4.0,
    }

    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    wallet_1 = WalletCreate(**wallet_data_1)
    wallet_2 = WalletCreate(**wallet_data_2)

    wallet_1 = await db.wallets.create_wallet(wallet_1, user_id=db_user.id)
    wallet_2 = await db.wallets.create_wallet(wallet_2, user_id=db_user.id)

    operation_1 = OperationCreate(**operation_data_1)
    operation_2 = OperationCreate(**operation_data_2)

    return db_user, wallet_1, wallet_2, operation_1, operation_2


async def test_get_all_operations(db: DBManager, user_wallets_operations):
    user, *_, operation_1, operation_2 = user_wallets_operations

    await OperationService(db).add_money(operation_1, user.id)
    await OperationService(db).add_money(operation_2, user.id)
    await OperationService(db).withdraw_money(operation_1, user.id)
    res = await OperationService(db).get_all_operations(
        "description", "desc", 0, 10, user.id
    )

    assert len(res) == 3
    assert isinstance(res[-1], OperationsHistory)


async def test_add_money(db: DBManager, user_wallets_operations):
    user, *_, operation_1, _ = user_wallets_operations

    res = await OperationService(db).add_money(operation_1, user.id)
    assert type(res) is dict


async def test_withdraw_money(db: DBManager, user_wallets_operations):
    user, *_, operation_1, _ = user_wallets_operations

    await OperationService(db).add_money(operation_1, user.id)
    res = await OperationService(db).withdraw_money(operation_1, user.id)
    assert res["message"] == "Wallet 'rub' balance decreased by 100.0"


async def test_transfer_money(db: DBManager, user_wallets_operations):
    user, *_, operation_1, operation_2 = user_wallets_operations

    transfer_data = {
        "wallet_from": "rub",
        "wallet_to": "usd",
        "amount": 50,
    }

    transfer = TransferMoneyCreate(**transfer_data)

    await OperationService(db).add_money(operation_1, user.id)
    res = await OperationService(db).transfer_money(transfer, user_id=user.id)

    assert isinstance(res, dict)
