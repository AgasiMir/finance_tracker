# # async def test_create_wallet(authenticated_ac):
# #     response = await authenticated_ac.post(
# #         "/api/v1/wallet/create_wallet",
# #         json={"name": "rub", "description": "main_wallet"},
# #     )
# #     assert response.status_code == 201

# async def test_get_wallets(authenticated_ac):
#     response = await authenticated_ac.get(
#         "/api/v1/wallet/my-wallets",
#         params={"page": 1, "page_size": 10},
#     )
#     print(response.json())


# async def test_get_wallet_by_name(authenticated_ac):
#     response = await authenticated_ac.get(
#         "/api/v1/wallet/my-wallets/rub",
#     )
#     assert response.status_code == 404


import pytest
from app.auth import create_access_token
from app.models.user import User


@pytest.fixture
async def get_token(db):
    db_user = User(email="user@example.com", hashed_password="1234abcdef")
    db.add(db_user)
    await db.commit()

    token = create_access_token(data={"sub": db_user.email, "id": db_user.id})

    return token


# async def test_get_empty_list_of_wallets(get_token, async_client):
#     token = get_token

#     response = await async_client.get(
#         "/api/v1/wallet/my-wallets",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert response.status_code == 200
#     assert response.json() == []


# async def test_get_not_existing_wallet_by_name(get_token, async_client):
#     token = get_token

#     response = await async_client.get(
#         "/api/v1/wallet/not_existing_wallet",
#         headers={"Authorization": f"Bearer {token}"},
#     )
#     assert response.status_code == 404


async def test_create_wallet(get_token, async_client):
    token = get_token

    response = await async_client.post(
        "/api/v1/wallet/create_wallet",
        json={"name": "rub"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    response = await async_client.get(
        "/api/v1/wallet/rub",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "rub"

    result = await async_client.get(
        "/api/v1/wallet/none",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert result.status_code == 404
