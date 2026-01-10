from random import choice

from fastapi import APIRouter, Query

from app.api.deps import DBSession, UserDep
from app.crud.crud_words import word_crud
from app.schemas.words import WordCreate, WordRead, WordUpdate
from app.services.favorites import FavoriteService
from app.services.typing import TypingService

router = APIRouter()


@router.get("", response_model=list[WordRead])
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
        skip=skip,
        limit=limit,
        category_ids=category_ids,
    )


@router.post("", response_model=WordRead, status_code=201)
async def create_words(
        session: DBSession,
        current_user: UserDep,
        word_in: WordCreate,
):
    return await word_crud.create_with_categories(db=session, obj_in=word_in)



@router.get("/random", response_model=WordRead)
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
        category_ids=category_ids,
    )
    word = choice(words)
    return word


@router.post("/check")
async def check_answer(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
        answer: str,
):
    return await TypingService.check_answer(
        session=session,
        word_id=word_id,
        answer=answer,
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
