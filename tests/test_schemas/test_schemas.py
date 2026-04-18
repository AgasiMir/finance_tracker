import pytest
from contextlib import nullcontext as does_not_raise
from pydantic import ValidationError
from app.schemas import (
    WalletPublic,
    WalletCreate,
    OperationCreate,
    TransferMoneyCreate,
    UserCreate,
)


@pytest.mark.parametrize(
    "id, name, balance, description, exc",
    [
        (1, "rub", 1000, "", does_not_raise()),
        (2, "usd", 20, "usd_wallet", does_not_raise()),
        (2.0, "usd", 20, "usd_wallet", does_not_raise()),
        ("2", "usd", 20, "usd_wallet", does_not_raise()),
        (2.2, "usd-3", 20, "usd_wallet", pytest.raises(ValidationError)),
        ("two", "usd", 20, "usd_wallet", pytest.raises(ValidationError)),
        (3, 14, 20, "usd_wallet", pytest.raises(ValidationError)),
        (3, [], 20, "usd_wallet", pytest.raises(ValidationError)),
        (3, "rub-2", {}, "usd_wallet", pytest.raises(ValidationError)),
    ],
)
async def test_wallet_public_schema(id, name, balance, description, exc):
    data = {"id": id, "name": name, "balance": balance, "description": description}
    with exc:
        WalletPublic(**data)


@pytest.mark.parametrize(
    "name, description, exc",
    [
        ("rub", "", does_not_raise()),
        ("usd", "usd_wallet", does_not_raise()),
        ("", "usd_wallet", pytest.raises(ValidationError)),
        ("  ", "", pytest.raises(ValidationError)),
    ],
)
async def test_wallet_create_schema(name, description, exc):
    data = {"name": name, "description": description}
    with exc:
        WalletCreate(**data)


@pytest.mark.parametrize(
    "wallet_name, amount, description, exc",
    [
        ("rub", 100, "", does_not_raise()),
        ("usd", 10, "usd_wallet", does_not_raise()),
        ("", 20, "usd_wallet", does_not_raise()),
        ("eur", 0, "", pytest.raises(ValidationError)),
        ("eur", -10, "", pytest.raises(ValidationError)),
        ("eur", 10, {}, pytest.raises(ValidationError)),
        ("eur", (), "", pytest.raises(ValidationError)),
    ],
)
async def test_operation_create_schema(wallet_name, amount, description, exc):
    data = {"wallet_name": wallet_name, "amount": amount, "description": description}
    with exc:
        OperationCreate(**data)


@pytest.mark.parametrize(
    "wallet_from, wallet_to, amount, exc",
    [
        ("rub", "rub-2", 100, does_not_raise()),
        ("rub", "rub-2", 0, pytest.raises(ValidationError)),
        ("rub", "rub-2", -100, pytest.raises(ValidationError)),
    ],
)
async def test_transfer_money_create_schema(wallet_from, wallet_to, amount, exc):
    data = {"wallet_from": wallet_from, "wallet_to": wallet_to, "amount": amount}
    with exc:
        TransferMoneyCreate(**data)


@pytest.mark.parametrize(
    "email, password, exc",
    [
        ("user@example.com", "12345678", does_not_raise()),
        ("user@example.com", "12345678" * 40, pytest.raises(ValidationError)),
        ("user@example.com", "1234567", pytest.raises(ValidationError)),
        ("user@example.com", {}, pytest.raises(ValidationError)),
        ("user@example", "12345678", pytest.raises(ValidationError)),
        ("userexample.com", "12345678", pytest.raises(ValidationError)),
        ([], "12345678", pytest.raises(ValidationError)),
    ],
)
async def test_user_create_schema(email, password, exc):
    with exc:
        UserCreate(email=email, password=password)
