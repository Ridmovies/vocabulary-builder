from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_words import word_crud


class TypingService:
    @staticmethod
    async def check_answer(session: AsyncSession, word_id: int, answer: str, user_id: int) -> dict:
        word = await word_crud.get_for_user(
            db=session,
            word_id=word_id,
            user_id=user_id,
        )

        is_correct = word.english.strip().lower() == answer.strip().lower()
        return {"correct": is_correct, "correct_word": word.english}