# app/core/settings.py
import secrets
from typing import Literal

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    MODE: Literal["DEV", "TEST", "PROD", "STAGING"]

    DATABASE_URL: str = "postgresql+asyncpg://postgres:root@localhost/vocabulary"

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
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"

    # Access токен
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 15 минут для безопасности
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    ACCESS_TOKEN_COOKIE_PATH: str = "/api"
    ACCESS_TOKEN_COOKIE_DOMAIN: str | None = None
    ACCESS_TOKEN_COOKIE_SECURE: bool = False  # True в production с HTTPS
    ACCESS_TOKEN_COOKIE_HTTPONLY: bool = True  # Защита от XSS
    ACCESS_TOKEN_COOKIE_SAMESITE: str = "lax"  # lax, strict, none

    # Refresh токен (опционально, но рекомендуется)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"

    # CSRF защита
    CSRF_TOKEN_COOKIE_NAME: str = "csrftoken"
    CSRF_TOKEN_HEADER_NAME: str = "X-CSRF-Token"
    CSRF_SECRET_KEY: str = secrets.token_urlsafe(32)

    # CORS (важно для кук!)
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:8000"]


settings = Settings()
