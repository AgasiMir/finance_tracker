import pytest
from app.auth import hash_password
from app.schemas import UserCreate
from app.models import User
from app.exceptions.python_exceptions import (
    UserAlreadyExistsException,
)
from app.uow.uow import DBManager


@pytest.fixture()
async def get_user(db: DBManager):
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

    db_user = User(email="user@example.com", hashed_password=hash_password("1234abcd"))
    db.add(db_user)
    await db.commit()

    return db_user


async def test_get_user_by_email(db: DBManager, get_user):
    user = get_user

    res = await db.users.get_user_by_email(user.email)
    assert res.email == "user@example.com"


async def test_create_user(db: DBManager):
    user = UserCreate(email="user@example.com", password="1234abcd")
    res = await db.users.create_user(user)
    assert res.email == "user@example.com"


async def test_create_user_with_the_same_email(db: DBManager, get_user):
    user = UserCreate(email="user@example.com", password="1234abcd")

    with pytest.raises(UserAlreadyExistsException):
        await db.users.create_user(user)


async def test_login_user(db: DBManager, get_user):
    user = get_user
    res = await db.users.login_user(user.email, "1234abcd")
    assert isinstance(res, dict)
    assert res.get("token_type") == "bearer"


async def test_refresh_token(db: DBManager, get_user):
    user = get_user
    res = await db.users.refresh_token(user.email)
    assert isinstance(res, dict)
    assert res.get("token_type") == "bearer"
