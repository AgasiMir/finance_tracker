from unittest.mock import patch

from app.exceptions.python_exceptions import (
    CredentialsException,
    UserAlreadyExistsException,
    IncorrectCredentialsException,
)


async def test_create_user(async_client):
    response = await async_client.post(
        "/api/v1/users/create-user",
        json={"email": "user@example.com", "password": "1234abcd"},
    )
    assert response.status_code == 201


async def test_login_user(async_client):
    await async_client.post(
        "/api/v1/users/create-user",
        json={"email": "user@example.com", "password": "1234abcd"},
    )
    response = await async_client.post(
        "/api/v1/users/token",
        data={"username": "user@example.com", "password": "1234abcd"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


async def test_refresh_token(async_client):
    await async_client.post(
        "/api/v1/users/create-user",
        json={"email": "user@example.com", "password": "1234abcd"},
    )

    response = await async_client.post(
        "/api/v1/users/token",
        data={"username": "user@example.com", "password": "1234abcd"},
    )

    refresh_token = response.json()["refresh_token"]

    res = await async_client.post(
        "/api/v1/users/refresh-token",
        json={"refresh_token": refresh_token},
    )

    assert res.status_code == 200
    assert "access_token" in res.json()
    assert "refresh_token" not in res.json()


async def test_create_user_that_already_exists(async_client):
    await async_client.post(
        "/api/v1/users/create-user",
        json={"email": "user@example.com", "password": "1234abcd"},
    )

    with patch("app.services.users.UserService.create_user") as mock_method:
        mock_method.side_effect = UserAlreadyExistsException

        response = await async_client.post(
            "/api/v1/users/create-user",
            json={"email": "user@example.com", "password": "12345abcde"},
        )

        assert response.status_code == 409
        mock_method.assert_called_once()


async def test_login_user_with_wrong_credentials(async_client):
    await async_client.post(
        "/api/v1/users/create-user",
        json={"email": "user@example.com", "password": "1234abcd"},
    )

    with patch("app.services.users.UserService.login") as mock_method:
        mock_method.side_effect = IncorrectCredentialsException

        response = await async_client.post(
            "/api/v1/users/token",
            data={"username": "user@example.com", "password": "1234abcd_"},
        )
        assert response.status_code == 401
        mock_method.assert_called_once()


async def test_refresh_token_with_wrong_refresh_token(async_client):
    await async_client.post(
        "/api/v1/users/create-user",
        json={"email": "user@example.com", "password": "1234abcd"},
    )

    response = await async_client.post(
        "/api/v1/users/token",
        data={"username": "user@example.com", "password": "1234abcd"},
    )

    refresh_token = response.json()["refresh_token"] + "abc"

    with patch("app.services.users.UserService.refresh_token") as mock_method:
        mock_method.side_effect = CredentialsException

        res = await async_client.post(
            "/api/v1/users/refresh-token",
            json={"refresh_token": refresh_token},
        )

        assert res.status_code == 401
