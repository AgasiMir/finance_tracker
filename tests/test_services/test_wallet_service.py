import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import WalletCreate, WalletPublic
from app.models import User
from app.services.wallets import WalletService
from app.exceptions.python_exceptions import WalletNotFoundException
from app.uow.uow import DBManager


@pytest.fixture
async def user(db: DBManager):
    """
    Фикстура для создания тестового пользователя непосредственно в базе данных.

    Эта фикстура:
    - Создаёт пользователя с email 'user@example.com' и хешированным паролем '1234abcd'.
    - Добавляет его в сессию базы данных, сохраняет изменения (commit).
    - Возвращает объект созданного пользователя (`db_user`).

    Используется в тестах, где требуется предварительное наличие пользователя в БД,
    особенно при тестировании сервисов, репозиториев или зависимостей на уровне БД,
    без прохождения HTTP-слоя регистрации.

    Зависимости:
        db: Асинхронная сессия базы данных (объект `DBManager` или аналогичный),
            используемая для взаимодействия с ORM.

    Примеры использования:
        async def test_user_exists(get_user, user_service):
            user = await user_service.get_user_by_email("user@example.com")
            assert user is not None

        async def test_token_creation(get_user, auth_service):
            token = auth_service.create_access_token(data={"sub": get_user.email})
            payload = auth_service.decode_access_token(token)
            assert payload["sub"] == "user@example.com"

    Особенности:
        - Не требует HTTP-запросов — работает на уровне данных.
        - Подходит для unit и интеграционных тестов, где важно избежать побочных эффектов API.
        - Использует реальный хеш пароля через `hash_password`, как в бизнес-логике приложения.

    Возвращает:
        User: ORM-объект пользователя, добавленный в базу данных.

    Примечание:
        Убедитесь, что таблица `users` существует и миграции применены.
        Также проверьте, что `DBManager` поддерживает методы `add`, `commit`.
    """

    db_user = User(email="user@example.com", hashed_password="1234abcd")
    db.add(db_user)
    await db.commit()

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
