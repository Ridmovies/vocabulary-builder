from fastapi import APIRouter

from app.api.deps import DBSession
from app.crud.crud_words import word_crud
from app.schemas.words import WordCreate, WordRead, WordUpdate

router = APIRouter()


@router.get("", response_model=list[WordRead])
async def get_words(session: DBSession):
    return await word_crud.get_multi(db=session)


@router.post("", response_model=WordRead, status_code=201)
async def create_words(
        session: DBSession,
        word_in: WordCreate,
):
    return await word_crud.create_with_categories(db=session, obj_in=word_in)



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
    return await word_crud.update(db=session, obj_in=word_in, db_obj=word)