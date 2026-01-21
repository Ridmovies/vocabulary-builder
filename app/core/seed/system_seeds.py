# app/core/seed/system_seeds.py
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models import Category, Word, word_category

SYSTEM_SEEDS_DIR = Path(__file__).parent / "system_dicts"

async def seed_system_categories(session: AsyncSession):
    for json_file in SYSTEM_SEEDS_DIR.glob("*.json"):
        data = json.loads(json_file.read_text(encoding="utf-8"))

        # --- Категория ---
        cat_data = data["category"]
        cat_name = cat_data["name"]

        result = await session.execute(
            select(Category).where(
                Category.name == cat_name,
                Category.owner_id == None
            )
        )
        category = result.scalar_one_or_none()
        if not category:
            category = Category(
                name=cat_data["name"],
                description=cat_data.get("description", "")
            )
            session.add(category)
            await session.flush()

        # --- Слова ---
        words_result = await session.execute(select(Word))
        existing_words = {w.english: w for w in words_result.scalars().all()}

        for w in data["words"]:
            word = existing_words.get(w["english"])
            if not word:
                word = Word(english=w["english"], russian=w["russian"])
                session.add(word)
                await session.flush()
                existing_words[w["english"]] = word

            # --- Добавляем связь напрямую через таблицу без конфликтов ---
            stmt = insert(word_category).values(
                word_id=word.id,
                category_id=category.id
            ).on_conflict_do_nothing(
                index_elements=["word_id", "category_id"]  # уникальные поля таблицы
            )

            await session.execute(stmt)

    await session.commit()
    print("✅ System categories seeded successfully!")