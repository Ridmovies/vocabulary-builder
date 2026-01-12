from fastapi import APIRouter

from app.api.deps import DBSession, UserDep
from app.crud.crud_catigory import category_crud
from app.schemas.category import CategoryRead, CategoryCreate

router = APIRouter()

from fastapi import Query

@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Получить категории",
    description=(
        "Возвращает список категорий, доступных пользователю:\n"
        "- системные категории (owner_id=None)\n"
        "- пользовательские категории (owner_id=current_user.id)\n"
        "Пагинация через skip/limit."
    )
)
async def get_categories(
    session: DBSession,
    current_user: UserDep,
    skip: int = Query(
        0,
        ge=0,
        description="Количество пропущенных категорий (offset)"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Максимальное количество категорий для возврата"
    )
):
    """
    Получить категории с учётом владельца.

    - Системные категории (`owner_id=None`)
    - Категории текущего пользователя (`owner_id=current_user.id`)
    """
    return await category_crud.get_multi_for_user(
        db=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )



@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(
        session: DBSession,
        current_user: UserDep,
        category_in: CategoryCreate,
):
    return await category_crud.create_for_user(
        db=session,
        obj_in=category_in,
        owner_id=current_user.id
    )



@router.delete("/{category_id}", status_code=204)
async def delete_category(
        session: DBSession,
        current_user: UserDep,
        category_id: int,
):
    return await category_crud.remove_for_user(db=session, category_id=category_id, owner_id=current_user.id)