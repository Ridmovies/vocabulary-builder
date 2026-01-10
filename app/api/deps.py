from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import decode_jwt_token, get_token_from_cookie, verify_csrf_token
from app.crud.crud_user import user_crud
from app.models import User


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


DBSession: type[AsyncSession] = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
        request: Request,
        db: AsyncSession = Depends(get_db),
        check_csrf: bool = True  # Проверять CSRF для опасных методов
) -> Optional[dict]:
    """
    Получить текущего пользователя из куки.

    Process:
    1. Получить access токен из куки
    2. Проверить CSRF токен (для POST/PUT/DELETE)
    3. Декодировать JWT
    4. Найти пользователя в БД
    5. Проверить активность
    """
    # 1. Получить токены из кук
    access_token = get_token_from_cookie(request, "access")

    if not access_token:
        return None

    # # 2. Проверка CSRF для опасных методов
    # if check_csrf and request.method in ["POST", "PUT", "PATCH", "DELETE"]:
    #     csrf_token = request.headers.get(settings.CSRF_TOKEN_HEADER_NAME)
    #     csrf_cookie = get_token_from_cookie(request, "csrf")
    #
    #     if not csrf_token or not csrf_cookie:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="CSRF токен отсутствует"
    #         )
    #
    #     if not verify_csrf_token(csrf_token, csrf_cookie):
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="Неверный CSRF токен"
    #         )

    # ПРОВЕРКА: если в разработке - пропускаем CSRF
    is_development = settings.MODE == "DEV"

    # Проверка CSRF (пропускаем в dev режиме)
    if (check_csrf and
            not is_development and  # ← Вот это важно!
            request.method in ["POST", "PUT", "PATCH", "DELETE"]):

        csrf_token = request.headers.get(settings.CSRF_TOKEN_HEADER_NAME)
        csrf_cookie = get_token_from_cookie(request, "csrf")

        if not csrf_token or not csrf_cookie:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF токен отсутствует"
            )

        if not verify_csrf_token(csrf_token, csrf_cookie):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Неверный CSRF токен"
            )

    # 3. Декодировать JWT
    payload = decode_jwt_token(access_token)

    if not payload or payload.get("type") != "access":
        return None

    # 4. Получить пользователя из БД
    user_id = payload.get("sub")
    if not user_id:
        return None

    user = await user_crud.get(db, id=int(user_id))

    if not user or not user.is_active:
        return None

    # 5. Обновить last_login (опционально)
    # Можно добавить здесь

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified
    }


# Аннотированный тип для зависимостей, представляющий текущего пользователя
UserDep: type[User] = Annotated[User, Depends(get_current_user)]