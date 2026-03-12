# app/core/settings.py
import secrets
from typing import Literal

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    MODE: Literal["DEV", "TEST", "PROD", "STAGING"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"

    DATABASE_URL: str
    TEST_DATABASE_URL: str

    # Разберем по частям:
    # postgresql+asyncpg://  - Используем PostgreSQL с async драйвером
    # username:password       - Логин и пароль для БД
    # @localhost              - Адрес сервера БД
    # /dbname                 - Название базы данных

    # Варианты:
    # - Локально: "postgresql+asyncpg://postgres:123456@localhost/vocabulary"
    # - В Docker: "postgresql+asyncpg://postgres:123456@postgres_db/vocabulary"
    # - В облаке: "postgresql+asyncpg://user:pass@aws.compute.amazonaws.com/db"

    # JWT настройки
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Access токен
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60000  # 15 минут для безопасности
    ACCESS_TOKEN_COOKIE_NAME: str = "access"
    ACCESS_TOKEN_COOKIE_PATH: str = "/"
    ACCESS_TOKEN_COOKIE_DOMAIN: str | None = None
    ACCESS_TOKEN_COOKIE_SECURE: bool = False  # True в production с HTTPS
    ACCESS_TOKEN_COOKIE_HTTPONLY: bool = True  # Защита от XSS
    ACCESS_TOKEN_COOKIE_SAMESITE: str = "lax"  # lax, strict, none

    # Refresh токен (опционально, но рекомендуется)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh"
    REFRESH_TOKEN_COOKIE_PATH: str = "/"

    # CSRF защита
    CSRF_TOKEN_COOKIE_NAME: str = "csrf"
    CSRF_TOKEN_COOKIE_PATH: str = "/"
    CSRF_TOKEN_HEADER_NAME: str = "X-CSRF-Token"
    CSRF_SECRET_KEY: str = secrets.token_urlsafe(32)

    # CORS (важно для кук!)
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:8000"]


    # VK OAUTH
    VK_OAUTH_CLIENT_ID: str | None = None
    # Защищённый ключ
    VK_OAUTH_CLIENT_SECRET: SecretStr | None = None
    VK_OAUTH_REDIRECT_URI: str | None = None

    # YANDEX CLOUD
    YANDEX_CLOUD_ACCESS_KEY: SecretStr
    YANDEX_CLOUD_SECRET_KEY: SecretStr
    YANDEX_CLOUD_ENDPOINT: str = "https://storage.yandexcloud.net"
    YANDEX_CLOUD_PUBLIC_BUCKET_NAME: str = "words-images"
    YANDEX_PRESIGNED_URL_EXPIRES_SECONDS: int = 300


settings = Settings()
