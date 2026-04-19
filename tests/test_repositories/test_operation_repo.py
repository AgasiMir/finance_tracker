import pytest
from app.schemas import (
    WalletCreate,
    OperationCreate,
    OperationsHistory,
    TransferMoneyCreate,
)
from app.models import User
from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    InsufficientFundsException,
    SameWalletException,
)

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


async def test_operation_add_money(db: DBManager, user_wallets_operations):
    user, *_, operation_1, operation_2 = user_wallets_operations

    res_1 = await db.operations.add_money(operation_1, user_id=user.id)
    res_2 = await db.operations.add_money(operation_2, user_id=user.id)

    assert isinstance(res_1, dict)
    assert res_2["new_balance"] == 4.0


async def test_operation_withdraw_money(db: DBManager, user_wallets_operations):
    user, *_, operation_1, _ = user_wallets_operations

    operation_data_2 = {
        "wallet_name": "rub",
        "amount": 50,
    }

    operation_2 = OperationCreate(**operation_data_2)

    await db.operations.add_money(operation_1, user_id=user.id)
    res = await db.operations.withdraw_money(operation_2, user_id=user.id)

    assert isinstance(res, dict)
    assert res["new_balance"] == operation_1.amount - operation_2.amount


async def test_operation_transfer_money(db: DBManager, user_wallets_operations):
    user, *_, operation_1, operation_2 = user_wallets_operations

    wallet_data_2 = {
        "name": "rub-2",
    }

    operation_data_2 = {
        "wallet_name": "rub-2",
        "amount": 1000,
    }

    transfer_data = {
        "wallet_from": "rub-2",
        "wallet_to": "rub",
        "amount": 500.0,
    }

    wallet_2 = WalletCreate(**wallet_data_2)

    await db.wallets.create_wallet(wallet_2, user_id=user.id)

    operation_2 = OperationCreate(**operation_data_2)

    await db.operations.add_money(operation_1, user_id=user.id)
    await db.operations.add_money(operation_2, user_id=user.id)

    transfer = TransferMoneyCreate(**transfer_data)

    res = await db.operations.transfer_money(transfer, user_id=user.id)

    assert isinstance(res, dict)


async def test_get_all_operations(db: DBManager, user_wallets_operations):
    user, *_, operation_1, operation_2 = user_wallets_operations

    await db.operations.add_money(operation_1, user_id=user.id)
    await db.operations.add_money(operation_2, user_id=user.id)

    res_1 = await db.operations.get_all_operations(
        "id",
        "desc",
        0,
        10,
        user.id,
    )
    res_2 = await db.operations.get_all_operations(
        "id",
        "desc",
        0,
        10,
        user.id,
        "expense",
    )
    assert len(res_1) == 2
    assert isinstance(res_1[0], OperationsHistory)
    assert len(res_2) == 0


async def test_add_money_to_not_existing_wallet(db: DBManager, user_wallets_operations):
    user, *_ = user_wallets_operations

    operation_data_1 = {
        "wallet_name": "not_existing_wallet",
        "amount": 100.0,
        "description": "bonus",
    }

    operation_1 = OperationCreate(**operation_data_1)

    with pytest.raises(WalletNotFoundException):
        await db.operations.add_money(operation_1, user_id=user.id)


async def test_withdraw_money_from_not_existing_wallet(
    db: DBManager, user_wallets_operations
):
    user, *_ = user_wallets_operations

    operation_data_1 = {
        "wallet_name": "not_existing_wallet",
        "amount": 100.0,
        "description": "bonus",
    }

    operation_1 = OperationCreate(**operation_data_1)

    with pytest.raises(WalletNotFoundException):
        await db.operations.withdraw_money(operation_1, user_id=user.id)


async def test_withdraw_money_with_insufficient_funds(
    db: DBManager, user_wallets_operations
):
    user, *_ = user_wallets_operations

    operation_data_1 = {
        "wallet_name": "rub",
        "amount": 200.0,
        "description": "bonus",
    }

    operation_1 = OperationCreate(**operation_data_1)

    with pytest.raises(InsufficientFundsException):
        await db.operations.withdraw_money(operation_1, user_id=user.id)


async def test_transfer_money_from_non_existing_wallet(
    db: DBManager, user_wallets_operations
):
    user, *_, operation_1, operation_2 = user_wallets_operations

    transfer_data = {
        "wallet_from": "not_existing_wallet",
        "wallet_to": "rub",
        "amount": 500.0,
    }

    await db.operations.add_money(operation_1, user_id=user.id)
    await db.operations.add_money(operation_2, user_id=user.id)

    transfer = TransferMoneyCreate(**transfer_data)

    with pytest.raises(WalletNotFoundException):
        await db.operations.transfer_money(transfer, user_id=user.id)


async def test_transfer_money_to_non_existing_wallet(
    db: DBManager, user_wallets_operations
):
    user, *_, operation_1, operation_2 = user_wallets_operations

    transfer_data = {
        "wallet_from": "rub",
        "wallet_to": "not_existing_wallet",
        "amount": 50,
    }

    await db.operations.add_money(operation_1, user_id=user.id)
    await db.operations.add_money(operation_2, user_id=user.id)

    transfer = TransferMoneyCreate(**transfer_data)

    with pytest.raises(WalletNotFoundException):
        await db.operations.transfer_money(transfer, user_id=user.id)


async def test_transfer_money_with_the_same_wallet(
    db: DBManager, user_wallets_operations
):
    user, *_, operation_1, operation_2 = user_wallets_operations

    transfer_data = {
        "wallet_from": "rub",
        "wallet_to": "rub",
        "amount": 50,
    }

    await db.operations.add_money(operation_1, user_id=user.id)
    await db.operations.add_money(operation_2, user_id=user.id)

    transfer = TransferMoneyCreate(**transfer_data)

    with pytest.raises(SameWalletException):
        await db.operations.transfer_money(transfer, user_id=user.id)


async def test_transfer_money_with_insufficient_funds(
    db: DBManager, user_wallets_operations
):
    user, *_, operation_1, operation_2 = user_wallets_operations

    transfer_data = {
        "wallet_from": "rub",
        "wallet_to": "usd",
        "amount": 500,
    }

    await db.operations.add_money(operation_1, user_id=user.id)
    await db.operations.add_money(operation_2, user_id=user.id)

    transfer = TransferMoneyCreate(**transfer_data)

    with pytest.raises(InsufficientFundsException):
        await db.operations.transfer_money(transfer, user_id=user.id)
