from typing import Optional, List

from sqlalchemy import select, or_, and_
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
            user_id: int,
            is_favorite: bool = False,
            category_ids: list[int] | None = None
    ) -> list[Word]:
        """
        Получить слова с пагинацией и фильтром по категориям.
        Слова берутся из категорий пользователя и системных категорий.
        """

        query = select(Word).offset(skip).limit(limit)
        query = query.options(selectinload(Word.categories))

        # 🔹 Если указаны категории, проверяем их владельцев
        if category_ids and user_id is not None:
            result = await db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            categories = result.scalars().all()

            # Проверяем, что все категории доступны пользователю или системные
            for cat in categories:
                if cat.owner_id not in (None, user_id):
                    raise ValueError(f"Категория {cat.id} недоступна пользователю")

            # Фильтруем слова по этим категориям
            query = query.join(Word.categories).where(Category.id.in_(category_ids))
        else:
            # Берём все свои категории + системные
            if user_id is not None:
                query = query.join(Word.categories).where(
                    or_(Category.owner_id == user_id, Category.owner_id.is_(None))
                )

        query = query.distinct()

        # 🔹 Только избранные слова
        if is_favorite:
            if not user_id:
                raise ValueError("user_id обязателен при is_favorite=True")
            query = query.join(favorite_words).where(favorite_words.c.user_id == user_id)

        result = await db.execute(query)
        return result.scalars().all()


    async def create_with_categories(
            self,
            db: AsyncSession,
            *,
            obj_in: WordCreate,
            owner_id: int,  # обязательно, т.к. слово создаётся пользователем
    ) -> Word:
        """
        Создать слово и связать его только с категориями текущего пользователя.
        """
        # 1. Создаём слово
        word_data = obj_in.model_dump(exclude={"category_ids"})
        word = Word(**word_data, owner_id=owner_id)

        # 2. Если есть категории — подгружаем и связываем
        if obj_in.category_ids:
            # Берём только категории пользователя
            result = await db.execute(
                select(Category).where(
                    Category.id.in_(obj_in.category_ids),
                    Category.owner_id == owner_id  # только свои категории
                )
            )
            categories = result.scalars().all()

            # Проверка: все указанные категории должны принадлежать пользователю
            if len(categories) != len(set(obj_in.category_ids)):
                raise ValueError("Все категории должны принадлежать текущему пользователю")

            word.categories.extend(categories)

        # 3. Сохраняем
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