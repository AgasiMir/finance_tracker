import pytest
from app.schemas import UserPublic, UserCreate
from app.models import User
from app.services.users import UserService
from app.exceptions.python_exceptions import (
    CredentialsException,
    UserAlreadyExistsException,
    IncorrectCredentialsException,
)
from app.uow.uow import DBManager
from app.auth import hash_password


@pytest.fixture
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


async def test_user_service_create_user(db: DBManager):
    user = UserCreate(email="user@example.com", password="1234abcd")
    user_service = UserService(db)
    res = await user_service.create_user(user)
    assert isinstance(res, UserPublic)


async def test_user_service_login_user(db: DBManager, get_user):
    user = get_user

    user_service = UserService(db)
    res = await user_service.login(user.email, "1234abcd")
    assert isinstance(res, dict)


async def test_user_service_login_user_with_incrorrect_credentials(
    db: DBManager, get_user
):
    user = get_user
    user_service = UserService(db)

    with pytest.raises(IncorrectCredentialsException):
        await user_service.login(user.email, "1234abcd_")


async def test_create_user_with_the_same_email(db: DBManager, get_user):
    user = UserCreate(email="user@example.com", password="1234abcd")
    user_service = UserService(db)

    with pytest.raises(UserAlreadyExistsException):
        await user_service.create_user(user)


async def test_service_refresh_token(db: DBManager, get_user):
    user = get_user
    user_service = UserService(db)
    data = await user_service.login(user.email, "1234abcd")

    res = await user_service.refresh_token(data["refresh_token"])
    assert isinstance(res, dict)


async def test_service_refresh_token_with_wrong_refresh_token(db: DBManager, get_user):
    user = get_user
    user_service = UserService(db)
    data = await user_service.login(user.email, "1234abcd")

    with pytest.raises(CredentialsException):
        await user_service.refresh_token(data["refresh_token"] + "abc")
