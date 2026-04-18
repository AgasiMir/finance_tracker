from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import WalletCreate
from app.models import Wallet, User


async def test_create_wallet(db: AsyncSession):
    data = {
        "name": "rub",
        "description": "main_wallet",
    }

    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    wallet = WalletCreate(**data)
    db_wallet = Wallet(**wallet.model_dump(), user_id=db_user.id)
    db.add(db_wallet)
    await db.commit()

    wallet = await db.scalar(select(Wallet))
    assert wallet.id == 1
    assert wallet.user_id == db_user.id


async def test_get_wallet_by_name(db: AsyncSession):
    data_1 = {
        "name": "rub",
        "description": "main_wallet",
    }

    data_2 = {
        "name": "usd",
        "description": None,
    }

    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    wallet = WalletCreate(**data_1)
    db_wallet = Wallet(**wallet.model_dump(), user_id=db_user.id)
    db.add(db_wallet)

    wallet = WalletCreate(**data_2)
    db_wallet = Wallet(**wallet.model_dump(), user_id=db_user.id)
    db.add(db_wallet)

    await db.commit()

    wallet = await db.scalar(select(Wallet).where(Wallet.name == "usd"))
    assert wallet.id == 2
    assert wallet.name != "rub"
    assert wallet.user_id == db_user.id


async def test_get_wallets(db: AsyncSession):
    data_1 = {
        "name": "rub",
        "description": "main_wallet",
    }

    data_2 = {
        "name": "usd",
        "description": None,
    }

    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.flush()

    wallet = WalletCreate(**data_1)
    db_wallet = Wallet(**wallet.model_dump(), user_id=db_user.id)
    db.add(db_wallet)

    wallet = WalletCreate(**data_2)
    db_wallet = Wallet(**wallet.model_dump(), user_id=db_user.id)
    db.add(db_wallet)

    await db.commit()

    wallets = await db.scalars(select(Wallet))
    assert len(wallets.all()) == 2
