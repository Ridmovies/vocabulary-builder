from fastapi import APIRouter

from app.api.deps import DBSession, UserDep
from app.crud.crud_catigory import category_crud
from app.schemas.category import CategoryRead, CategoryCreate

router = APIRouter()

from fastapi import Query

@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Список категорий",
    description=(
        "Возвращает категории пользователя.\n\n"
        "Типы:\n"
        "- system — системные\n"
        "- mine — пользовательские\n"
        "- all — все доступные\n\n"
        "Поддерживает пагинацию."
    )
)
async def get_categories(
    session: DBSession,
    current_user: UserDep,
    scope: str = Query(
        "all",
        description="Фильтр категорий: all | system | mine"
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Смещение (offset)"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Лимит записей"
    )
):
    """Получить список категорий."""
    return await category_crud.get_multi_for_user(
        db=session,
        user_id=current_user.id,
        scope=scope,
        skip=skip,
        limit=limit
    )


@router.post(
    "",
    response_model=CategoryRead,
    status_code=201,
    summary="Создать категорию",
    description="Создаёт категорию для текущего пользователя."
)
async def create_category(
    session: DBSession,
    current_user: UserDep,
    category_in: CategoryCreate,
):
    """Создать новую категорию."""
    return await category_crud.create_for_user(
        db=session,
        obj_in=category_in,
        owner_id=current_user.id
    )


@router.delete(
    "/{category_id}",
    status_code=204,
    summary="Удалить категорию",
    description="Удаляет категорию пользователя по ID."
)
async def delete_category(
    session: DBSession,
    current_user: UserDep,
    category_id: int
):
    """Удалить категорию."""
    return await category_crud.remove_for_user(
        db=session,
        category_id=category_id,
        owner_id=current_user.id
    )