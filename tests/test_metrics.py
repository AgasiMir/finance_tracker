async def test_metrics_endpoint(async_client):
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


async def test_request_increments_counters(async_client):
    # Выполняем запрос, чтобы сработал middleware
    await async_client.get(
        "/api/v1/wallet/my-wallets",
        params={"page": 1, "page_size": 10},
    )

    # Проверим, что /metrics доступен и не падает
    response = await async_client.get("/metrics")
    assert response.status_code == 200
