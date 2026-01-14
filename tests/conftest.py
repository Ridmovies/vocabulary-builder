"""
Принципы:

    Один тест — одна ответственность — тест проверяет одну вещь
    ARRANGE-ACT-ASSERT паттерн
    Изоляция тестов — тесты не должны зависеть друг от друга
    Читаемые имена — test_create_user_with_valid_data()
"""


import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.api.deps import get_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:root@localhost/vocab_test"
)

engine_test = create_async_engine(
    url=TEST_DATABASE_URL,
    poolclass = NullPool,  # ключевой момент для тестов
)

AsyncSessionTest = async_sessionmaker(
    engine_test,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    # Создаём таблицы один раз для всей сессии
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # drop_all необязательно, можно оставить



@pytest.fixture(scope="function")
async def db_session():
    """
    Каждый тест получает отдельный connection и транзакцию.
    Данные автоматически откатываются.
    """
    async with engine_test.connect() as conn:  # отдельный connection
        async with conn.begin():  # глобальная транзакция
            session = AsyncSessionTest(bind=conn)
            yield session
            # откат всей транзакции после теста
            await conn.rollback()


@pytest.fixture(scope="function", autouse=True)
async def override_get_db_fixture(db_session: AsyncSession):
    """
    Переопределяет Depends(get_db) для всех эндпоинтов, чтобы
    они использовали db_session фикстуры.
    """
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()



@pytest.fixture
async def async_client():
    # ASGITransport использует текущий asyncio loop pytest-asyncio
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client