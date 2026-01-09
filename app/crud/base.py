# app/crud/base.py

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

# Тип переменные для дженериков
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс CRUD операций.

    Args:
        model: SQLAlchemy модель
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Получить объект по ID.

        Args:
            db: Сессия базы данных
            id: ID объекта

        Returns:
            Объект модели или None
        """
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
            self,
            db: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100
    ) -> List[ModelType]:
        """
        Получить несколько объектов с пагинацией.

        Args:
            db: Сессия базы данных
            skip: Количество объектов для пропуска
            limit: Максимальное количество объектов

        Returns:
            Список объектов
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Создать новый объект.

        Args:
            db: Сессия базы данных
            obj_in: Pydantic схема с данными

        Returns:
            Созданный объект
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Обновить объект.

        Args:
            db: Сессия базы данных
            db_obj: Объект из базы данных
            obj_in: Pydantic схема или словарь с данными для обновления

        Returns:
            Обновленный объект
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        Удалить объект.

        Args:
            db: Сессия базы данных
            id: ID объекта для удаления

        Returns:
            Удаленный объект или None
        """
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def count(self, db: AsyncSession) -> int:
        """
        Подсчитать количество объектов.

        Args:
            db: Сессия базы данных

        Returns:
            Количество объектов
        """
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        result = await db.execute(query)
        return result.scalar()