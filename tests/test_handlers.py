async def test_check_db_connection(async_client):
    response = await async_client.get("handlers/check-db")
    assert response.status_code == 200
    assert "PostgreSQL" in response.text
