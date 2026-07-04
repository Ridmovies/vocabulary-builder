from random import choice

from fastapi import APIRouter, Query, HTTPException
from starlette import status

from app.api.deps import DBSession, UserDep
from app.crud.crud_words import word_crud
from app.schemas.typing import TypingCheckRequest
from app.schemas.words import WordRead
from app.services.typing import TypingService

router = APIRouter()



@router.get(
    "/random",
    response_model=WordRead,
    summary="Случайное слово",
    description=(
        "Возвращает случайное слово пользователя.\n\n"
        "Поддерживает:\n"
        "- пагинацию\n"
        "- фильтр по категориям\n\n"
        "Если слова не найдены — 404."
    )
)
async def get_random_word(
    session: DBSession,
    current_user: UserDep,
    skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
    category_ids: list[int] | None = Query(
        None, description="Фильтр по категориям, список ID"
    ),
):
    """
    Получить слова с пагинацией и фильтром по категориям.
    """
    words = await word_crud.get_multi_with_categories(
        db=session,
        skip=skip,
        limit=limit,
        user_id=current_user.id,
        category_ids=category_ids,
    )
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В выбранной категории нет слов"
        )

    return choice(words)


@router.post(
    "/check",
    summary="Проверка ответа",
    description="Проверяет правильность введённого перевода слова."
)
async def check_answer(
    request: TypingCheckRequest,
    session: DBSession,
    current_user: UserDep,
):
    return await TypingService.check_answer(
        session=session,
        word_id=request.word_id,
        answer=request.answer,
        user_id=current_user.id,
    )