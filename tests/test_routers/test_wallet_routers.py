import pytest
from unittest.mock import patch
from app.auth import create_access_token
from app.schemas import UserCreate
from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)


@pytest.fixture
async def get_token(db):
    """
    Фикстура для прямого создания JWT-токена доступа для тестового пользователя.

    Эта фикстура:
    - Создаёт тестового пользователя в базе данных с email 'user@example.com'.
    - Генерирует JWT-токен с полями 'sub' (email) и 'id' (идентификатор пользователя).
    - Возвращает только токен (без настройки клиента).

    Является альтернативой фикстуре `authenticated_ac` в случаях, когда:
        - Нужно получить токен без выполнения реального запроса к /api/v1/users/token.
        - Требуется протестировать логику обработки токена вне HTTP-слоя.
        - Упрощается тестирование внутренних зависимостей (например, `get_current_user`).

    Зависимости:
        db: Асинхронная сессия базы данных (например, Tortoise ORM или SQLAlchemy AsyncSession),
            используемая для сохранения пользователя.

    Пример использования:
        async def test_decode_token(get_token):
            payload = decode_access_token(get_token)
            assert payload["sub"] == "user@example.com"

        async def test_protected_route_with_manual_header(async_client, get_token):
            async_client.headers["Authorization"] = f"Bearer {get_token}"
            response = await async_client.get("/api/v1/users/me")
            assert response.status_code == 200

    Важно:
        - Эта фикстура не создаёт клиент и не управляет HTTP-сессией.
        - Подходит для unit-тестов и сценариев, где нужен только токен.
        - Использует ту же логику генерации токена, что и основное приложение (`create_access_token`).

    Возвращает:
        str: Строка JWT-токена для тестового пользователя.
    """

    user = UserCreate(email="user@example.com", password="1234abcdef")
    db_user = await db.users.create_user(user)
    await db.commit()

    token = create_access_token(data={"sub": db_user.email, "id": db_user.id})

    return token


async def test_get_empty_list_of_wallets(get_token, async_client):
    response = await async_client.get(
        "/api/v1/wallets/my-wallets",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_get_list_of_wallets_with_pagination(get_token, async_client):
    await async_client.post(
        "/api/v1/wallets/create-wallet",
        json={"name": "rub"},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    await async_client.post(
        "/api/v1/wallets/create-wallet",
        json={"name": "usd"},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    response = await async_client.get(
        "/api/v1/wallets/my-wallets",
        headers={"Authorization": f"Bearer {get_token}"},
        params={"page": 2, "page_size": 1},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "usd"


async def test_get_wallet_by_name(get_token, async_client):
    await async_client.post(
        "/api/v1/wallets/create-wallet",
        json={"name": "rub"},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    response = await async_client.get(
        "/api/v1/wallets/rub",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "rub"


async def test_create_wallet(get_token, async_client):
    response = await async_client.post(
        "/api/v1/wallets/create-wallet",
        json={"name": "rub"},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    assert response.status_code == 201


async def test_get_not_existing_wallet_by_name(get_token, async_client):
    wallet_name = "not_existing_wallet"
    response = await async_client.get(
        f"/api/v1/wallets/{wallet_name}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404
    response_data = response.json()
    assert f"Wallet {wallet_name!r} Not Found" == response_data["detail"]


async def test_get_not_existing_wallet_by_name_2(get_token, async_client):
    wallet_name = "not_existing_wallet"

    with patch("app.services.wallets.WalletService.get_wallet_by_name") as mock_method:
        mock_method.side_effect = WalletNotFoundException(wallet_name)

        response = await async_client.get(
            f"/api/v1/wallets/{wallet_name}",
            headers={"Authorization": f"Bearer {get_token}"},
        )

        assert response.status_code == 404
        mock_method.assert_called_once()


async def test_create_wallets_with_the_same_name(get_token, async_client):
    await async_client.post(
        "/api/v1/wallets/create-wallet",
        json={"name": "rub"},
        headers={"Authorization": f"Bearer {get_token}"},
    )

    with patch("app.services.wallets.WalletService.create_wallet") as mock_method:
        mock_method.side_effect = WalletAlreadyExistsException

        response = await async_client.post(
            "/api/v1/wallets/create-wallet",
            json={"name": "rub"},
            headers={"Authorization": f"Bearer {get_token}"},
        )

        assert response.status_code == 409
        mock_method.assert_called_once()
