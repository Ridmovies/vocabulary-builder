from typing import List

from fastapi import APIRouter, Query

from app.api.deps import DBSession
from app.crud.crud_words import word_crud
from app.schemas.words import WordCreate, WordRead, WordUpdate

router = APIRouter()


# @router.get("", response_model=list[WordRead])
# async def get_words(session: DBSession):
#     return await word_crud.get_multi_with_categories(db=session)

@router.get("", response_model=List[WordRead])
async def get_words(
    session: DBSession,
    skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
    category_ids: List[int] | None = Query(
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
        word_in: WordCreate,
):
    return await word_crud.create_with_categories(db=session, obj_in=word_in)



@router.get("/{word_id}", response_model=WordRead)
async def get_word(
        session: DBSession,
        word_id: int,
):
    return await word_crud.get(db=session, id=word_id)


@router.delete("/{word_id}", status_code=204)
async def delete_words(
        session: DBSession,
        word_id: int,
):
    return await word_crud.remove(db=session, id=word_id)



@router.put("/{word_id}", response_model=WordRead)
async def update_words(
        session: DBSession,
        word_id: int,
        word_in: WordUpdate,
):
    # Получаем слово
    word = await word_crud.get(db=session, id=word_id)
    return await word_crud.update_with_categories(db=session, obj_in=word_in, db_obj=word)