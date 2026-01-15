from random import choice

from fastapi import APIRouter, Query, HTTPException
from starlette import status

from app.api.deps import DBSession, UserDep
from app.crud.crud_words import word_crud
from app.schemas.typing import TypingCheckRequest
from app.schemas.words import WordCreate, WordRead, WordUpdate
from app.services.favorites import FavoriteService
from app.services.typing import TypingService

router = APIRouter()


@router.get(
    "",
    response_model=list[WordRead],
    summary="Получить слова с фильтром и пагинацией",
    description=(
            "Фильтр по категориям. Можно указать список ID категорий. "
            "Возвращаются только слова из системных категорий (owner_id=None) и ваших категорий."
    ),
)
async def get_words(
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
    return await word_crud.get_multi_with_categories(
        db=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        category_ids=category_ids,
    )


@router.post(
    "",
    response_model=WordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое слово",
    description=(
        "Создаёт новое слово и связывает его с категориями текущего пользователя.\n\n"
        "- Пользователь может добавлять слово **только в свои категории**.\n"
        "- Системные или чужие категории использовать нельзя.\n"
        "- Возвращает созданное слово с его категориями."
    ),
)
async def create_words(
    session: DBSession,
    current_user: UserDep,
    word_in: WordCreate,
):
    """
    Создать слово с привязкой к категориям пользователя.
    """
    return await word_crud.create_with_categories(
        db=session,
        obj_in=word_in,
        owner_id=current_user.id
    )



@router.get(
    "/random",
    response_model=WordRead,
    description="""
    ### Фильтры (query-параметры):
    - **is_favorite** — фильтр по избранным (`true` или `false`).
    """
)
async def get_random_word(
        session: DBSession,
        current_user: UserDep,
        skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
        limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
        is_favorite: bool | None = Query(None, description="Фильтр по избранным"),
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
        is_favorite=is_favorite,
        user_id=current_user.id,
        category_ids=category_ids,
    )
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В выбранной категории нет слов"
        )

    return choice(words)


@router.post("/check")
async def check_answer(
        session: DBSession,
        current_user: UserDep,
        request: TypingCheckRequest  # Получаем из body
):
    return await TypingService.check_answer(
        session=session,
        word_id=request.word_id,
        answer=request.answer,
    )

@router.get("/favorites", response_model=list[WordRead])
async def get_favorites(
    session: DBSession,
    current_user: UserDep,
):
    return await FavoriteService.get_favorites(
        session=session,
        user_id=current_user.id,
    )


@router.get("/{word_id}", response_model=WordRead)
async def get_word(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
):
    return await word_crud.get(db=session, id=word_id)


@router.delete("/{word_id}", status_code=204)
async def delete_words(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
):
    return await word_crud.remove(db=session, id=word_id)



@router.put("/{word_id}", response_model=WordRead)
async def update_words(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
        word_in: WordUpdate,
):
    # Получаем слово
    word = await word_crud.get(db=session, id=word_id)
    return await word_crud.update_with_categories(db=session, obj_in=word_in, db_obj=word)


@router.post("/favorites/{word_id}")
async def add_to_favorites(
    word_id: int,
    session: DBSession,
    current_user: UserDep,
):
    await FavoriteService.add_to_favorites(
        session=session,
        user_id=current_user.id,
        word_id=word_id,
    )
    return {"status": "added"}


@router.delete("/favorites/{word_id}")
async def remove_from_favorites(
    word_id: int,
    session: DBSession,
    current_user: UserDep,
):
    await FavoriteService.remove_from_favorites(
        session=session,
        user_id=current_user.id,
        word_id=word_id,
    )
    return {"status": "removed"}
