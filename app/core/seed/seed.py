import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models import User
from app.models.word import Word
from app.models.category import Category
from app.utils.pwd import get_password_hash

USERS = [
    {"email": "user@example.com", "username": "user", "password": "string", "is_superuser": False},
    {"email": "alice@example.com", "username": "alice", "password": "password123", "is_superuser": False},
    {"email": "bob@example.com", "username": "bob", "password": "password123", "is_superuser": False},
    {"email": "charlie@example.com", "username": "charlie", "password": "password123", "is_superuser": False},
]

# --- Данные для сида ---
CATEGORIES = [
    {"name": "Basic", "description": "Самые простые слова"},
    {"name": "Food", "description": "Еда и напитки"},
    {"name": "Animals", "description": "Животные"},
    {"name": "difficult", "description": "Сложные слова"},
    {"name": "phrasal verbs", "description": "Фразовый глагол"},
    {"name": "default", "description": "Категория по умолчанию"},
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
    {"english": "arrangement", "russian": "договоренность", "categories": ["difficult"]},
    {"english": "take off", "russian": "снимать (одежду), взлетать", "categories": ["phrasal verbs"]},
    {"english": "turn on", "russian": "включать", "categories": ["phrasal verbs"]},
    {"english": "turn off", "russian": "выключать", "categories": ["phrasal verbs"]},
    {"english": "get up", "russian": "вставать", "categories": ["phrasal verbs"]},
    {"english": "go on", "russian": "продолжать", "categories": ["phrasal verbs"]},
    {"english": "come back", "russian": "возвращаться", "categories": ["phrasal verbs"]},
]

USER_DEFAULT_WORDS = [
    {"english": "entire", "russian": "целый, весь"},
    {"english": "concerned", "russian": "обеспокоенный"},
    {"english": "anxious", "russian": "тревожный"},
    {"english": "coincidence", "russian": "совпадение"},
    {"english": "fate", "russian": "судьба"},
    {"english": "despite", "russian": "несмотря на"},
    {"english": "get out", "russian": "выходить, убираться"},
    {"english": "intend", "russian": "намереваться"},
    {"english": "severe", "russian": "серьёзный, суровый"},
    {"english": "damp", "russian": "сырой, влажный"},
    {"english": "suffer", "russian": "страдать"},
    {"english": "significant", "russian": "значительный"},
    {"english": "eventually", "russian": "в конечном итоге"},
    {"english": "on purpose", "russian": "намеренно"},
    {"english": "frustration", "russian": "разочарование"},
]

# Добавляем USER_DEFAULT_WORDS в WORDS с категорией default
WORDS.extend(
    {
        "english": w["english"],
        "russian": w["russian"],
        "categories": ["default"],
    }
    for w in USER_DEFAULT_WORDS
)


async def seed():
    async with AsyncSessionLocal() as session:
        async with session.begin():

            # --- Создаём категории ---
            existing_cats = {}
            for cat in CATEGORIES:
                result = await session.execute(
                    select(Category).where(Category.name == cat["name"])
                )
                existing_cat = result.scalar_one_or_none()
                if existing_cat:
                    existing_cats[cat["name"]] = existing_cat
                else:
                    new_cat = Category(name=cat["name"], description=cat["description"])
                    session.add(new_cat)
                    await session.flush()  # id появится сразу
                    existing_cats[cat["name"]] = new_cat

            # --- Создаём слова ---
            existing_words = {}
            result = await session.execute(select(Word))
            for w in result.scalars().all():
                existing_words[w.english] = w

            for w in WORDS:
                word = existing_words.get(w["english"])
                if not word:
                    word = Word(
                        english=w["english"],
                        russian=w["russian"],
                        categories=[],  # пустой список сразу
                    )
                    session.add(word)
                    await session.flush()
                    existing_words[w["english"]] = word

                # Добавляем категории
                for cat_name in w["categories"]:
                    if cat_name in existing_cats and existing_cats[cat_name] not in word.categories:
                        word.categories.append(existing_cats[cat_name])

        await session.commit()
    print("Seed completed!")



async def seed_users():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем всех существующих пользователей
            existing_users = await session.execute(select(User))
            existing_users = {u.email: u for u in existing_users.scalars().all()}

            for u in USERS:
                if u["email"] not in existing_users:
                    hashed_password = get_password_hash(u["password"])
                    user_obj = User(
                        email=u["email"],
                        username=u["username"],
                        hashed_password=hashed_password,
                        is_superuser=u["is_superuser"],
                        is_active=True,
                        is_verified=True,  # можно выставить True для сида
                    )
                    session.add(user_obj)

        await session.commit()
    print("User seed completed!")


if __name__ == "__main__":
    asyncio.run(seed())
    asyncio.run(seed_users())
