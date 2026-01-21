from sqlalchemy import select
from app.models import Word, Category
from app.core.database import AsyncSessionLocal

WORDS = [
    {"english": "hello", "russian": "привет", "categories": ["Basic"]},
    {"english": "entire", "russian": "целый", "categories": ["default"]},
]


async def seed_words():
    async with AsyncSessionLocal() as session:
        async with session.begin():

            # Загружаем категории ОДИН раз
            result = await session.execute(select(Category))
            categories = {c.name: c for c in result.scalars().all()}

            # Загружаем существующие слова
            result = await session.execute(select(Word))
            existing = {w.english: w for w in result.scalars().all()}

            new_words = []

            for w in WORDS:
                if w["english"] in existing:
                    continue

                word = Word(
                    english=w["english"],
                    russian=w["russian"],
                    categories=[
                        categories[cat_name]
                        for cat_name in w["categories"]
                        if cat_name in categories
                    ],
                )

                new_words.append(word)

            session.add_all(new_words)

