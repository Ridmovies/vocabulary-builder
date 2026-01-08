from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import word_category
from app.models.word import Word
from app.schemas.words import WordCreate, WordUpdate


class CRUDWord(CRUDBase[Word, WordCreate, WordUpdate]):
    """
    CRUD операции для модели Word.
    Наследуемся от базового класса и добавляем специфичные методы.
    """

    async def create_with_categories(
            self,
            db: AsyncSession,
            *,
            obj_in: WordCreate,
            # user_id: int
    ) -> Word:
        """
        Создать слово с категориями.
        """
        from app.models.category import Category

        # 1. Извлекаем данные для слова
        word_data = obj_in.model_dump(exclude={"category_ids"})
        # word_data["user_id"] = user_id

        # 2. Создаем объект слова
        db_obj = Word(**word_data)
        db.add(db_obj)
        await db.commit()  # Сначала коммитим слово
        await db.refresh(db_obj)  # Обновляем объект

        # 3. Добавляем категории, если они указаны
        if obj_in.category_ids:
            # Получаем объекты категорий
            categories_query = select(Category).where(
                Category.id.in_(obj_in.category_ids)
            )
            categories_result = await db.execute(categories_query)
            categories = categories_result.scalars().all()

            # ВАЖНО: Получаем текущий объект из сессии
            # Иначе категории будут в detached состоянии
            word = await self.get(db, id=db_obj.id)

            # Добавляем категории
            word.categories.extend(categories)
            db.add(word)
            await db.commit()
            await db.refresh(word)

            return word

        return db_obj

word_crud = CRUDWord(Word)