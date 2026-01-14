"""
Принципы:

    Один тест — одна ответственность — тест проверяет одну вещь
    ARRANGE-ACT-ASSERT паттерн
    Изоляция тестов — тесты не должны зависеть друг от друга
    Читаемые имена — test_create_user_with_valid_data()
"""


import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client