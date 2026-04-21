async def test_check_db_connection(async_client):
    response = await async_client.get("health/check-db")
    assert response.status_code == 200
    assert "version" in response.json()
