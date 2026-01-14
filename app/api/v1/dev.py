from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DBSession
from app.core.database import engine
from app.models import Base

router = APIRouter()


@router.get("")
async def root():
    return {"message": "Hello World"}


@router.get("/check-database")
async def check_db(
        session: DBSession
):
    """
    Проверка подключения к базе данных.

    Выполняет простой SQL запрос к БД и возвращает статус.
    """

    # Выполняем простой запрос "SELECT 1"
    # Это стандартный способ проверить соединение
    result = await session.execute(text("SELECT 1"))

    # Получаем результат
    data = result.scalar()  # Получит число 1

    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2024-01-15T12:00:00Z",
        "query_result": data
    }

@router.get("/db-info")
async def db_info(session: DBSession):
    engine = session.get_bind()

    return {
        "dialect": engine.dialect.name,
        "driver": engine.dialect.driver,
        "url": str(engine.url),
    }

@router.delete("/reset-database")
async def reset_db():
    async with engine.begin() as conn:
        # Полное удаление всех таблиц
        await conn.run_sync(Base.metadata.drop_all)
        # Создание всех таблиц заново
        await conn.run_sync(Base.metadata.create_all)