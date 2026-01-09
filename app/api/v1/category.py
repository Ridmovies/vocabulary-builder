from fastapi import APIRouter

from app.api.deps import DBSession
from app.crud.crud_catigory import category_crud
from app.schemas.category import CategoryRead, CategoryCreate

router = APIRouter()

@router.get("", response_model=list[CategoryRead])
async def get_categories(
        session: DBSession
):
    return await category_crud.get_multi(db=session)


@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(
        session: DBSession,
        category_in: CategoryCreate,
):
    return await category_crud.create(db=session, obj_in=category_in)



@router.delete("/{category_id}", status_code=204)
async def delete_category(
        session: DBSession,
        category_id: int,
):
    return await category_crud.remove(db=session, id=category_id)