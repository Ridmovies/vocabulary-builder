import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.word import Word
from app.models.category import Category

# --- Данные для сида ---
CATEGORIES = [
    {"name": "Basic", "description": "Самые простые слова"},
    {"name": "Food", "description": "Еда и напитки"},
    {"name": "Animals", "description": "Животные"},
]

WORDS = [
    {"english": "hello", "russian": "привет", "categories": ["Basic"]},
    {"english": "goodbye", "russian": "пока", "categories": ["Basic"]},
    {"english": "cat", "russian": "кот", "categories": ["Animals"]},
    {"english": "dog", "russian": "собака", "categories": ["Animals"]},
    {"english": "apple", "russian": "яблоко", "categories": ["Food"]},
    {"english": "bread", "russian": "хлеб", "categories": ["Food"]},
    {"english": "milk", "russian": "молоко", "categories": ["Food"]},
    {"english": "water", "russian": "вода", "categories": ["Food"]},
    {"english": "sun", "russian": "солнце", "categories": ["Basic"]},
    {"english": "moon", "russian": "луна", "categories": ["Basic"]},
    {"english": "bird", "russian": "птица", "categories": ["Animals"]},
    {"english": "fish", "russian": "рыба", "categories": ["Animals"]},
    {"english": "egg", "russian": "яйцо", "categories": ["Food"]},
    {"english": "cheese", "russian": "сыр", "categories": ["Food"]},
    {"english": "watermelon", "russian": "арбуз", "categories": ["Food"]},
    {"english": "horse", "russian": "лошадь", "categories": ["Animals"]},
    {"english": "tree", "russian": "дерево", "categories": ["Basic"]},
    {"english": "book", "russian": "книга", "categories": ["Basic"]},
    {"english": "chair", "russian": "стул", "categories": ["Basic"]},
    {"english": "bread", "russian": "хлеб", "categories": ["Food"]},  # дубликат для примера
]

async def seed():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # --- Сначала категории ---
            existing_cats = await session.execute(select(Category))
            existing_cats = {c.name: c for c in existing_cats.scalars().all()}

            for cat in CATEGORIES:
                if cat["name"] not in existing_cats:
                    new_cat = Category(name=cat["name"], description=cat["description"])
                    session.add(new_cat)
                    existing_cats[cat["name"]] = new_cat

            await session.flush()  # чтобы были id категорий

            # --- Теперь слова ---
            existing_words = await session.execute(select(Word))
            existing_words = {w.english: w for w in existing_words.scalars().all()}

            for w in WORDS:
                if w["english"] not in existing_words:
                    word_obj = Word(
                        english=w["english"],
                        russian=w["russian"]
                    )
                    # Связь с категориями
                    word_obj.categories = [existing_cats[c] for c in w["categories"] if c in existing_cats]
                    session.add(word_obj)

        await session.commit()
    print("Seed completed!")

if __name__ == "__main__":
    asyncio.run(seed())
