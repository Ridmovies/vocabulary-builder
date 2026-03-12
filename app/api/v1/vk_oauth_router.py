from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, RedirectResponse

from app.api.deps import DBSession
from app.core.config import settings
from app.core.logger import logger
from app.core.security import set_auth_cookies
from app.services.vk_oauth_service import VKOAuthService

router = APIRouter()

@router.get(
    "/vk/get_auth_url",
    summary="""
    Логин через ВК.
    Получить ссылку для авторизации через VK ID, для не авторизованных пользователей.
    Используется после привязки внутреннего аккаунта к VK ID.
    """,
    description="""
    Генерирует ссылку на VK ID авторизацию с использованием PKCE (Proof Key for Code Exchange) и параметра `state`.

    **Что делает метод:**
    - Формирует полный URL для авторизации VK.
    - Возвращает ссылку, на которую фронтенд должен **перенаправить пользователя**.

    **Как использовать на фронте:**
    1. Вызвать этот метод с бэкенда.
    2. Получить `auth_url` из ответа.
    3. Перенаправить пользователя на этот `auth_url`.
    4. После успешного логина VK отправит пользователя на `redirect_uri`, указанный в настройках приложения.

    **PKCE:**
    PKCE добавляет дополнительный уровень безопасности, чтобы предотвратить кражу кода авторизации.
    """,
    response_description="Ссылка для авторизации VK ID для не авторизованных пользователей",
    response_class=JSONResponse,
)
async def get_vk_auth_url():
    """
    Шаг 1: Генерация ссылки на VK ID авторизацию (PKCE + state)
    """
    auth_url = await VKOAuthService.get_vk_auth_url()
    return {"auth_url": auth_url}



@router.get(
    "/callback/vkontakte",
    summary="⚠️ Не используется. Callback от VK OAuth",
    status_code=status.HTTP_200_OK,
)
async def callback_vk(

    session: DBSession,
    code: str,
    state: str,
    device_id: str,
):
    """
    """
    logger.debug(f"Финальный callback от VK OAuth после успешной авторизации")
    logger.debug(f"{code=}")
    logger.debug(f"{state=}")
    logger.debug(f"{device_id=}")
    vk_access_token = await VKOAuthService.get_access_token_from_code(
        code=code,
        state=state,
        device_id=device_id,
    )

    tokens = await VKOAuthService.register_or_login_vk(session=session, vk_access_token=vk_access_token)

    logger.debug(f"{tokens=}")

    response = RedirectResponse(url=settings.FRONTEND_URL)

    set_auth_cookies(
        response=response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        csrf_token=tokens["csrf_token"],
    )

    return response
