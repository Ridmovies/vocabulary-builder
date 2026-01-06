from fastapi import APIRouter

from app.api.deps import DBSession
from app.crud.crud_words import word_crud
from app.schemas.words import WordCreate

router = APIRouter()


@router.get("")
async def get_words():
    pass


@router.post("")
async def create_words(
        session: DBSession,
        word_in: WordCreate,
):
    return  await word_crud.create(db=session, obj_in=word_in)