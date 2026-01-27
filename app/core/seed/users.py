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
        {"english": "look down on", "russian": "смотреть свысока, презирать"},
        {"english": "approach", "russian": "подход, приближение"},
        {"english": "envy", "russian": "зависть, завидовать"},
        {"english": "exhaust", "russian": "истощать, выматывать"},
        {"english": "belong", "russian": "принадлежать"},
        {"english": "after having / being", "russian": "после того как (что-то сделав / будучи кем-то)"},
        {"english": "frantic", "russian": "панический, неистовый"},
        {"english": "affirmation", "russian": "подтверждение, утверждение"},
        {"english": "tend to", "russian": "иметь склонность"},
        {"english": "offensive", "russian": "оскорбительный, наступательный"},
        {"english": "hit it off", "russian": "сразу поладить"},
        {"english": "convinced", "russian": "убеждённый"},
        {"english": "necessary", "russian": "необходимый"},
        {"english": "confident", "russian": "уверенный"},
        {"english": "treatment", "russian": "лечение, обращение"},
        {"english": "deserve", "russian": "заслуживать"},
        {"english": "refuse", "russian": "отказываться"},
        {"english": "get it", "russian": "понимать, уловить"},
        {"english": "maintenance", "russian": "обслуживание, содержание, поддержание"},
        {"english": "afford", "russian": "позволить себе"},
        {"english": "relieved", "russian": "испытывающий облегчение"},
        {"english": "struggles", "russian": "трудности, борьба"},
        {"english": "let someone down", "russian": "подвести кого-то"},
        {"english": "took place", "russian": "произошло, имело место"},
        {"english": "miserable", "russian": "несчастный, жалкий"},
        {"english": "beneath", "russian": "под, ниже; недостойно"},
        {"english": "cuisine", "russian": "кухня (национальная)"},
        {"english": "tray", "russian": "поднос"},
        {"english": "be considered", "russian": "считаться, рассматриваться"},
        {"english": "is seeing", "russian": "встречается с, видится"},
        {"english": "stare", "russian": "пристально смотреть, уставиться"},
        {"english": "aside from", "russian": "кроме, помимо"},
        {"english": "took place", "russian": "произошло, имело место"},
        {"english": "claim", "russian": "утверждать, претендовать; заявление, претензия"},
        {"english": "clue", "russian": "ключ к разгадке, подсказка"},
        {"english": "awkward", "russian": "неловкий, неудобный"},
        {"english": "suspended", "russian": "приостановленный, подвешенный"},
        {"english": "maintain", "russian": "поддерживать, сохранять"},
        {"english": "fit in with", "russian": "соответствовать, гармонировать с"},
        {"english": "get into a mess", "russian": "вляпаться, попасть в неприятности"},
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
