from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.api.deps import DBSession
from app.services.vk_oauth_service import VKOAuthService

router = APIRouter()


@router.post(
    "",
    summary="Создание аккаунта или вход",

)
async def vk_register_or_login():
    pass



@router.get(
    "/vk/get_auth_url",
    summary="""
    ⚠️ Не используется
    Логин через ВК.
    Получить ссылку для авторизации через VK ID, для не авторизованных пользователей.
    Используется после привязки внутреннего аккаунта к VK ID.
    Инструкция: /src/dev_only/docs/vk_oauth_run_in_docker.md
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
    description="""
    Финальный callback от VK OAuth после успешной авторизации.

    — Используется фронтендом, не работает через Swagger (переадресация).

    Возвращает access/refresh токены для дальнейшей работы.
    """,
    responses={
        400: {
            "description": "Ошибка авторизации",
            "content": {
                "application/json": {"example": {"detail": "Ошибка авторизации"}}
            },
        },
    },
    response_class=JSONResponse,
)
async def callback_vk(
    session: DBSession,
    code: str,
    state: str,
    device_id: str,
):
    return await VKOAuthService.exchange_codes_for_vk_tokens(
        session=session,
        code=code,
        state=state,
        device_id=device_id,
    )
