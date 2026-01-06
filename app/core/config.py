# app/core/settings.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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


settings = Settings()
