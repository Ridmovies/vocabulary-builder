from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.api.deps import DBSession
from app.core.logger import logger
from app.services.vk_oauth_service import VKOAuthService

router = APIRouter()

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
)
async def callback_vk(
    session: DBSession,
    code: str,
    state: str,
    device_id: str,
):
    """
    Регистрация или вход пользователя через VK OAuth.

    Алгоритм работы:

    1. Получение информации о пользователе через VK API используя vk_access_token:
       - user_id, email, имя, фамилия, пол, аватар, день рождения.

    2. Подготовка данных для локальной модели пользователя:
       - Если email отсутствует, генерируется временный email на основе vk_id.
       - Генерируется уникальный username.
       - Создаётся случайный криптографический пароль и хешируется.

    3. Проверка существования аккаунта:
       a) По vk_id через OAuthAccountRepository.
          - Если найден, используется связанный пользователь.
       b) Если vk_id не найден, проверяется существующий пользователь по email.
          - Если найден, привязывается VK OAuth аккаунт к существующему пользователю.
       c) Если пользователь не найден, создаётся новый пользователь с подготовленными данными и привязывается VK OAuth аккаунт.

    4. Создание локального JWT access_token для пользователя с использованием внутренней функции create_access_token.

    5. Возврат словаря с ключом "access_token", который используется frontend для аутентификации с backend.

    Особенности:

    - Пользователь не получает пароль напрямую; для обычного входа требуется отдельный флоу установки пароля.
    - Метод обеспечивает единый вход/регистрацию через VK, сохраняя бизнес-инварианты (email обязательный).
    - Логирование debug уровня фиксирует этапы поиска и привязки аккаунта, но не содержит чувствительные токены VK.
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

    return await VKOAuthService.register_or_login_vk(
        session=session,
        vk_access_token=vk_access_token,
    )
