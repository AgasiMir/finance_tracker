import time
from locust import HttpUser, task, between
import random
import uuid


# Перед запуском нагрузочного тестирования, нужно отключить rate limiter у ручек
"locust -f locustfile.py --host=http://localhost:8000"


class FinanceTrackerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Генерируем уникальные данные для каждого пользователя Locust
        self.user_id = str(uuid.uuid4())[:8]
        self.email = f"test_{self.user_id}@example.com"
        self.password = "password123"

        # 1. Создаем пользователя
        create_response = self.client.post(
            "/api/v1/users/create-user",
            json={
                "email": self.email,
                "password": self.password,
            },
        )

        if create_response.status_code not in [201, 400]:
            # Если ошибка не "пользователь уже существует", логируем
            print(
                f"Failed to create user: {create_response.status_code} - {create_response.text}"
            )

        # 2. Логинимся для получения токена (OAuth2 форма)
        login_response = self.client.post(
            "/api/v1/users/token",
            data={"username": self.email, "password": self.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if login_response.status_code == 200:
            self.token = login_response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"User {self.email} authenticated successfully")
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            # Если логин не удался, создаем заглушку чтобы тесты не падали
            self.token = None
            self.headers = {}

        # Создаем кошелек rub
        self.client.post(
            "/api/v1/wallets/create-wallet",
            headers=self.headers,
            json={"name": "rub"},
        )

        # Создаем кошелек usd
        self.client.post(
            "/api/v1/wallets/create-wallet",
            headers=self.headers,
            json={"name": "usd"},
        )

    @task(8)
    def get_operations(self):
        if not self.token:
            return
        self.client.get(
            "/api/v1/operations/my-operations",
            headers=self.headers,
            params={"sort": "amount", "dir": "DESC", "offset": 0, "limit": 10},
        )

    @task(4)
    def get_wallet_by_name(self):
        if not self.token:
            return
        self.client.get(
            "/api/v1/wallets/rub",
            headers=self.headers,
        )

    @task(4)
    def get_wallet_by_name_2(self):
        if not self.token:
            return
        self.client.get(
            "/api/v1/wallets/usd",
            headers=self.headers,
        )

    @task(8)
    def get_wallets(self):
        if not self.token:
            return
        self.client.get(
            "/api/v1/wallets/my-wallets",
            headers=self.headers,
        )

    @task(1)
    def create_wallet(self):
        """
        Каждый пользователь создает 20 кошельков
        Чтобы не было конфликтов в названии, к названию кошелька прибалвяется
        случайное число в заданном диапозоне
        """
        if not self.token:
            return

        for _ in range(1, 20):
            time.sleep(0.5)
            self.client.post(
                "/api/v1/wallets/create-wallet",
                headers=self.headers,
                json={"name": "rub" + str(random.randint(1, 1_000_000))},
            )

    @task(1)
    def add_money(self):
        if not self.token:
            return

        self.client.post(
            "/api/v1/operations/add",
            headers=self.headers,
            json={"wallet_name": "rub", "amount": 1000},
        )
