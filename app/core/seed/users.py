import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models import User, Category, Word, word_category
from app.utils.pwd import get_password_hash

USERS = [
    {"email": "user@example.com", "username": "user", "password": "string"},
    {"email": "user2@example.com", "username": "user2", "password": "string"},
    {"email": "user3@example.com", "username": "user3", "password": "string"},
    {"email": "mom@example.com", "username": "mom", "password": "string"},
]

USER_DEFAULT_WORDS = {
    "user@example.com": [
        {"english": "entire", "russian": "целый, весь"},
        {"english": "unconscious", "russian": "бессознательный, без сознания"},
    ],

    "user2@example.com": [
        {"english": "cat", "russian": "кот"},
        {"english": "dog", "russian": "собака"},
    ],
    "user3@example.com": [
        {"english": "sun", "russian": "солнце"},
        {"english": "moon", "russian": "луна"},
    ],
}

logger = logging.getLogger("seed")
logging.basicConfig(level=logging.INFO)

async def seed_users(session: AsyncSession):
    # --- существующие пользователи ---
    result = await session.execute(select(User))
    existing_users = {u.email: u for u in result.scalars().all()}
    logger.info(f"Found {len(existing_users)} existing users.")

    # --- существующие слова ---
    result = await session.execute(select(Word))
    existing_words = {w.english: w for w in result.scalars().all()}
    logger.info(f"Found {len(existing_words)} existing words.")

    for u in USERS:
        user = existing_users.get(u["email"])
        if not user:
            user = User(
                email=u["email"],
                username=u["username"],
                hashed_password=get_password_hash(u["password"]),
                is_superuser=False,
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            await session.flush()
            existing_users[u["email"]] = user
            logger.info(f"Created user: {u['email']}")
        else:
            logger.info(f"User exists: {u['email']}")

        # --- категория default ---
        result = await session.execute(
            select(Category).where(
                Category.owner_id == user.id,
                Category.name == "default",
            )
        )
        category = result.scalar_one_or_none()
        if not category:
            category = Category(
                name="default",
                description="Категория по умолчанию",
                owner_id=user.id,
            )
            session.add(category)
            await session.flush()
            logger.info(f"Created default category for user: {u['email']}")
        else:
            logger.info(f"Default category exists for user: {u['email']}")

        # --- личные слова ---
        for w in USER_DEFAULT_WORDS.get(u["email"], []):
            word = existing_words.get(w["english"])
            if not word:
                word = Word(
                    english=w["english"],
                    russian=w["russian"],
                )
                session.add(word)
                await session.flush()
                existing_words[w["english"]] = word
                logger.info(f"Created word: {w['english']}")
            else:
                logger.info(f"Word exists: {w['english']}")

            stmt = insert(word_category).values(
                word_id=word.id,
                category_id=category.id,
            ).on_conflict_do_nothing(
                index_elements=["word_id", "category_id"]
            )
            await session.execute(stmt)
            logger.info(f"Linked word '{word.english}' to category '{category.name}'")

    await session.commit()
    logger.info("✅ Users seeded with default categories and words!")

    await session.commit()
    print("✅ Users seeded with default categories and words!")
