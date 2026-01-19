from fastapi import APIRouter
from starlette.responses import Response

from app.api.deps import DBSession
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate, UserRead
from app.services.users import UserService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    response: Response,
    user_in: UserCreate,
    session: DBSession,
):
    """
    Регистрация нового пользователя.
    """
    return await UserService.register_user(
        db=session,
        obj_in=user_in,
    )

    # return await user_crud.create(db=session, obj_in=user_in)