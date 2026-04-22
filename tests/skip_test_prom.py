# tests/test_metrics_middleware.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_request_increments_counters():
    # Выполняем запрос, чтобы сработал middleware
    client.get("/api/v1/wallet/my-wallets?page=1&page_size=10")

    # Проверим, что /metrics доступен и не падает
    response = client.get("/metrics")
    assert response.status_code == 200
