from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: Literal["DEV", "TEST", "PROD"] = "DEV"

    DB_DRIVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    SECRET_KEY: str
    ALGORITHM: str

    GF_SECURITY_ADMIN_USER: str
    GF_SECURITY_ADMIN_PASSWORD: str

    authentication_backend_secret_key: str

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_PORT: int
    RABBITMQ_DEFAULT_HOST: str

    MailDEV_HOST: str

    @property
    def RABBITMQ_URL(self):
        url = f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_DEFAULT_HOST}:{self.RABBITMQ_DEFAULT_PORT}/"
        return url

    @property
    def DB_URL(self):
        url = f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return url

    model_config = SettingsConfigDict(env_file=[".env.dev"])


settings = Settings()
