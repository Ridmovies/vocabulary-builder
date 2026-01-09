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
    ) -> Word:
        from app.models.category import Category

        # 1. Создаём слово
        word_data = obj_in.model_dump(exclude={"category_ids"})
        word = Word(**word_data)

        # 2. Если есть категории — подгружаем и связываем
        if obj_in.category_ids:
            result = await db.execute(
                select(Category).where(Category.id.in_(obj_in.category_ids))
            )
            categories = result.scalars().all()

            if len(categories) != len(set(obj_in.category_ids)):
                raise ValueError("One or more categories not found")

            word.categories.extend(categories)

        # 3. Один add + один commit
        db.add(word)
        await db.commit()
        await db.refresh(word)

        return word


word_crud = CRUDWord(Word)