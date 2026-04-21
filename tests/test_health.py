import pytest


from app.auth import create_access_token, hash_password
from app.models.user import User
from app.uow.uow import DBManager


@pytest.fixture
async def admin_user(db: DBManager):
    db_user = User(
        email="admin@example.com",
        hashed_password=hash_password("1234abcd"),
        role="admin",
    )
    db.add(db_user)
    await db.commit()

    token = create_access_token(data={"sub": db_user.email, "id": db_user.id})

    return token


async def test_check_db_connection_not_authorized(authenticated_ac):
    response = await authenticated_ac.get("health/check-db")
    assert response.status_code == 403


async def test_check_db_connection_authorized(async_client, admin_user):
    response = await async_client.get(
        "health/check-db",
        headers={"Authorization": f"Bearer {admin_user}"},
    )
    assert response.status_code == 200
    assert "version" in response.json()
