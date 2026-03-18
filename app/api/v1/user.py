from fastapi import APIRouter
from starlette.responses import Response

from app.api.deps import DBSession
from app.schemas.user import UserCreate, UserRead
from app.services.users import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="Регистрация пользователя",
    description="Создаёт нового пользователя и возвращает его данные."
)
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