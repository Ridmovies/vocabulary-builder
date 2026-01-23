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
        {"english": "tend (to)", "russian": "иметь склонность"},
        {"english": "offensive", "russian": "оскорбительный, наступательный"},
        {"english": "hit it off", "russian": "сразу поладить"},

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

async def seed_users(session: AsyncSession):
    async with session.begin():

        # --- существующие пользователи ---
        result = await session.execute(select(User))
        existing_users = {u.email: u for u in result.scalars().all()}

        # --- существующие слова ---
        result = await session.execute(select(Word))
        existing_words = {w.english: w for w in result.scalars().all()}

        for u in USERS:
            if u["email"] in existing_users:
                continue

            # --- пользователь ---
            user = User(
                email=u["email"],
                username=u["username"],
                hashed_password=get_password_hash(u["password"]),
                is_superuser=False,
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            await session.flush()  # получаем user.id

            # --- дефолтная категория ---
            category = Category(
                name="default",
                description="Категория по умолчанию",
                owner_id=user.id,
            )
            session.add(category)
            await session.flush()  # получаем category.id

            # --- личные слова пользователя ---
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

                stmt = insert(word_category).values(
                    word_id=word.id,
                    category_id=category.id,
                ).on_conflict_do_nothing(
                    index_elements=["word_id", "category_id"]
                )

                await session.execute(stmt)

    print("✅ Users seeded with default categories and words!")
