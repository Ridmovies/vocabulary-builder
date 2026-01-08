from fastapi import APIRouter

from app.api.deps import DBSession
from app.crud.crud_catigory import category_crud

router = APIRouter()

@router.get("")
async def get_categories(
        session: DBSession
):
    return await category_crud.get_multi(db=session)