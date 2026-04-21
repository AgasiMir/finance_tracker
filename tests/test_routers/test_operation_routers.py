import asyncio
import pytest
from unittest.mock import patch

from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    InsufficientFundsException,
    SameWalletException,
)


@pytest.fixture
async def wallets(authenticated_ac):
    """
    Фикстура для создания двух тестовых кошельков через API.

    Эта фикстура:
    - Использует уже авторизованный клиент (`authenticated_ac`).
    - Создаёт два кошелька с именами 'rub' и 'rub-2' через POST-запрос к `/api/v1/wallet/create-wallet`.
    - Не возвращает значение, а просто гарантирует, что кошельки существуют перед запуском теста.

    Используется в тестах операций (пополнение, снятие, перевод), где требуется предварительная
    настройка пользовательских кошельков.

    Зависимости:
        authenticated_ac: Асинхронный HTTP-клиент с установленной авторизацией.

    Пример использования:
        async def test_add_money(authenticated_ac, wallets):
            # Кошельки 'rub' и 'rub-2' уже созданы фикстурой `wallets`
            response = await authenticated_ac.post(
                "/api/v1/operations/add",
                json={"wallet_name": "rub", "amount": 100}
            )
            assert response.status_code == 201

    Важно:
        - Фикстура имеет область видимости по умолчанию 'function', т.е. выполняется для каждого теста.
        - Имена кошельков ('rub', 'rub-2') захардкожены — при изменении логики имён нужно обновить и тесты.
        - Не проверяет статус ответа; если создание кошелька упадёт — упадёт и тест (что ожидаемо).

    Предназначена для интеграционных тестов маршрутов, связанных с операциями над кошельками.
    """
    await authenticated_ac.post(
        "/api/v1/wallet/create-wallet",
        json={"name": "rub"},
    )

    await authenticated_ac.post(
        "/api/v1/wallet/create-wallet",
        json={"name": "rub-2"},
    )


async def test_get_my_operations(authenticated_ac, wallets):
    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    await asyncio.sleep(1)

    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub-2", "amount": 2000},
    )

    response = await authenticated_ac.get(
        "/api/v1/operations/my-operations",
        params={"sort": "amount", "dir": "ASC"},
    )
    assert response.status_code == 200
    assert response.json()[-1]["amount"] == 2000


async def test_add_money(authenticated_ac, wallets):
    response = await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    assert response.status_code == 201
    assert response.json()["new_balance"] == 100


async def test_withdraw_money(authenticated_ac, wallets):
    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    response = await authenticated_ac.post(
        "/api/v1/operations/withdraw",
        json={"wallet_name": "rub", "amount": 50},
    )

    assert response.status_code == 201
    assert response.json()["new_balance"] == 50


async def test_transfer_money(authenticated_ac, wallets):
    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    response = await authenticated_ac.post(
        "/api/v1/operations/transfer",
        json={"wallet_from": "rub", "wallet_to": "rub-2", "amount": 50},
    )

    assert response.status_code == 201


async def test_add_money_to_non_existing_wallet(authenticated_ac, wallets):
    wallet_name = "rub"

    with patch("app.services.operations.OperationService.add_money") as mock_method:
        mock_method.side_effect = WalletNotFoundException(wallet_name)

        response = await authenticated_ac.post(
            "/api/v1/operations/add",
            json={"wallet_name": f"{wallet_name}", "amount": 100},
        )

        assert response.status_code == 404
        mock_method.assert_called_once()


async def test_withdraw_money_from_non_existing_wallet(authenticated_ac, wallets):
    wallet_name = "non_existing_wallet"

    with patch(
        "app.services.operations.OperationService.withdraw_money"
    ) as mock_method:
        mock_method.side_effect = WalletNotFoundException(wallet_name)

        response = await authenticated_ac.post(
            "/api/v1/operations/withdraw",
            json={"wallet_name": "rub", "amount": 50},
        )

        assert response.status_code == 404
        mock_method.assert_called_once()


async def test_withdraw_money_with_insufficient_funds(authenticated_ac, wallets):
    with patch(
        "app.services.operations.OperationService.withdraw_money"
    ) as mock_method:
        mock_method.side_effect = InsufficientFundsException("rub", 100)

        response = await authenticated_ac.post(
            "/api/v1/operations/withdraw",
            json={"wallet_name": "rub", "amount": 500},
        )

        assert response.status_code == 400
        mock_method.assert_called_once()


async def test_transfer_money_from_non_existing_wallet(authenticated_ac, wallets):
    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    with patch(
        "app.services.operations.OperationService.transfer_money"
    ) as mock_method:
        mock_method.side_effect = WalletNotFoundException("rub-3")

        response = await authenticated_ac.post(
            "/api/v1/operations/transfer",
            json={"wallet_from": "rub-3", "wallet_to": "rub-2", "amount": 50},
        )

        assert response.status_code == 404
        mock_method.assert_called_once()


async def test_transfer_money_with_insufficient_funds(authenticated_ac, wallets):
    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    with patch(
        "app.services.operations.OperationService.transfer_money"
    ) as mock_method:
        mock_method.side_effect = InsufficientFundsException("rub", 100)

        response = await authenticated_ac.post(
            "/api/v1/operations/transfer",
            json={"wallet_from": "rub-3", "wallet_to": "rub-2", "amount": 500},
        )

        assert response.status_code == 400
        mock_method.assert_called_once()


async def test_transfer_money_with_the_same_wallet(authenticated_ac, wallets):
    await authenticated_ac.post(
        "/api/v1/operations/add",
        json={"wallet_name": "rub", "amount": 100},
    )

    with patch(
        "app.services.operations.OperationService.transfer_money"
    ) as mock_method:
        mock_method.side_effect = SameWalletException

        response = await authenticated_ac.post(
            "/api/v1/operations/transfer",
            json={"wallet_from": "rub-3", "wallet_to": "rub-2", "amount": 500},
        )

        assert response.status_code == 400
        mock_method.assert_called_once()
