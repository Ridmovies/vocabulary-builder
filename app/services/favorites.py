from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Word


class FavoriteService:

    @staticmethod
    async def add_to_favorites(
        session: AsyncSession,
        user_id: int,
        word_id: int,
    ):
        user = await session.get(User, user_id)
        word = await session.get(Word, word_id)

        if not user or not word:
            raise ValueError("User or Word not found")

        if word not in user.favorite_words:
            user.favorite_words.append(word)
            await session.commit()

        return True

    @staticmethod
    async def remove_from_favorites(
        session: AsyncSession,
        user_id: int,
        word_id: int,
    ):
        user = await session.get(User, user_id)
        word = await session.get(Word, word_id)

        if word in user.favorite_words:
            user.favorite_words.remove(word)
            await session.commit()

        return True

    @staticmethod
    async def get_favorites(
        session: AsyncSession,
        user_id: int,
    ):
        stmt = (
            select(Word)
            .join(Word.favorited_by)
            .where(User.id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalars().all()