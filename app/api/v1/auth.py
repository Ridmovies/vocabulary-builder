from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from app.api.deps import DBSession, UserDep
from app.core.security import set_auth_cookies, create_access_token, create_refresh_token, create_csrf_token, \
    clear_auth_cookies
from app.crud.crud_user import user_crud
from app.schemas.user import UserLogin, UserRead

router = APIRouter()


@router.post("/login")
async def login(
        response: Response,
        request: Request,
        user_in: UserLogin,
        session: DBSession,
):
    """
    Вход пользователя.

    Устанавливает:
    - access_token в HTTP-only куке
    - refresh_token в HTTP-only куке (опционально)
    - csrf_token в обычной куке (доступен JS)
    """
    # 1. Аутентификация
    user = await user_crud.authenticate(
        db=session,
        email=user_in.email,
        password=user_in.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email/пароль"
        )

    # 2. Создаем токены
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email
    )

    refresh_token = create_refresh_token(user_id=user.id)

    # 3. Создаем CSRF токен
    csrf_token = create_csrf_token()

    # 4. Устанавливаем куки
    set_auth_cookies(
        response=response,
        access_token=access_token,
        refresh_token=refresh_token,
        csrf_token=csrf_token
    )

    # 5. Обновляем last_login
    # Можно добавить здесь

    return {"access_token": access_token, "refresh_token": refresh_token, "csrf_token": csrf_token}


@router.post("/logout")
async def logout(
        response: Response,
        current_user: UserDep
):
    """
    Выход пользователя.

    Удаляет все аутентификационные куки.
    """
    clear_auth_cookies(response)

    return {"message": "Успешный выход"}


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: UserDep,
    session: DBSession,
):
    """
    Получить информацию о текущем пользователе.
    """
    return await user_crud.get(db=session, id=current_user.id)



# @router.post("/refresh")
# async def refresh(
#     request: Request,
#     response: Response,
#     session: DBSession,
# ):
#     """
#     Обновление access_token по refresh_token из cookie.
#     """
#
#     # 1. Достаем refresh_token из cookie
#     refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
#
#     if not refresh_token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Refresh token missing",
#         )
#
#     # 2. Валидируем refresh_token (нужна твоя функция decode/verify)
#     try:
#         payload = user_crud.verify_refresh_token(refresh_token)
#         user_id: int = payload.get("sub")
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#         )
#
#     # 3. Проверяем пользователя
#     user = await user_crud.get(db=session, id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found",
#         )
#
#     # 4. Генерируем новые токены
#     new_access_token = create_access_token(
#         user_id=user.id,
#         username=user.username,
#         email=user.email,
#     )
#
#     # rotation refresh (рекомендуется)
#     new_refresh_token = create_refresh_token(user_id=user.id)
#
#     new_csrf_token = create_csrf_token()
#
#     # 5. Перезаписываем куки
#     set_auth_cookies(
#         response=response,
#         access_token=new_access_token,
#         refresh_token=new_refresh_token,
#         csrf_token=new_csrf_token,
#     )
#
#     return {"status": "ok"}