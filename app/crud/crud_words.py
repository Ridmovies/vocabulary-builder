from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import word_category, Category, favorite_words
from app.models.word import Word
from app.schemas.words import WordCreate, WordUpdate


class CRUDWord(CRUDBase[Word, WordCreate, WordUpdate]):
    """
    CRUD операции для модели Word.
    Наследуемся от базового класса и добавляем специфичные методы.
    """

    async def get_multi_with_categories(
            self,
            db: AsyncSession,
            *,
            skip: int = 0,
            limit: int = 100,
            user_id : Optional[int] = None,
            is_favorite : bool = False,
            category_ids: list[int] | None = None
    ) -> list[Word]:
        query = select(Word).offset(skip).limit(limit)
        query = query.options(selectinload(Word.categories))

        if category_ids:
            query = query.join(Word.categories).where(Category.id.in_(category_ids)).distinct()

        # 🔹 Только избранные слова пользователя
        if is_favorite:
            if not user_id:
                raise ValueError("user_id обязателен при is_favorite=True")

            query = (
                query
                .join(favorite_words)
                .where(favorite_words.c.user_id == user_id)
            )

        result = await db.execute(query)
        return result.scalars().all()


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

    async def update_with_categories(
            self,
            db: AsyncSession,
            *,
            db_obj: Word,
            obj_in: WordUpdate
    ) -> Word:

        # 1. Обновляем простые поля
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in ["english", "russian"]:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        # 2. Обновляем категории, если пришли
        if "category_ids" in update_data:
            result = await db.execute(
                select(Category).where(Category.id.in_(update_data["category_ids"]))
            )
            categories = result.scalars().all()
            db_obj.categories = categories  # перезаписываем связи

        # 3. Сохраняем
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


word_crud = CRUDWord(Word)