from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import User, Word
from app.crud.crud_words import word_crud


class FavoriteService:

    @staticmethod
    async def add_to_favorites(
        session: AsyncSession,
        user_id: int,
        word_id: int,
    ):
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        word = await word_crud.get_for_user(
            db=session,
            word_id=word_id,
            user_id=user_id,
        )

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
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        word = await word_crud.get_for_user(
            db=session,
            word_id=word_id,
            user_id=user_id,
        )

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