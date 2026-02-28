import base64
import hashlib
import secrets
import time
import urllib.parse

import httpx

from fastapi import HTTPException
from fastapi.logger import logger
from starlette.requests import Request
from starlette.responses import Response

from app.api.deps import DBSession
from app.core.config import settings


# словарь для хранения state
_state_store = {}  # {state: {"data": storage_data, "ts": timestamp}}

class VKOAuthService:
    """
    Сервис для работы с VK OAuth
    """
    # Конфигурация VK OAuth
    client_id = settings.VK_OAUTH_CLIENT_ID
    client_secret = settings.VK_OAUTH_CLIENT_SECRET.get_secret_value()
    vk_redirect_uri = settings.VK_OAUTH_REDIRECT_URI


    @staticmethod
    def _get_state_key(state: str) -> str:
        """Ключ для хранения временных данных OAuth в Redis"""
        return f"vk_auth:state:{state}"

    @staticmethod
    def generate_pkce_pair():
        """Генерация пары PKCE"""
        code_verifier = secrets.token_urlsafe(64)[:128]
        code_challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )
        return code_verifier, code_challenge

    @staticmethod
    async def set_params(mode: str, user_id: int | None):
        """Установка параметров авторизации и сохранение их в Redis"""
        code_verifier, code_challenge = VKOAuthService.generate_pkce_pair()
        state = secrets.token_urlsafe(16)

        storage_data = {
            "code_verifier": code_verifier,
            "mode": mode,
            "user_id": user_id,
        }
        # сохраняем с меткой времени
        _state_store[state] = {"data": storage_data, "ts": time.time()}

        params = {
            "response_type": "code",
            "client_id": VKOAuthService.client_id,
            "redirect_uri": VKOAuthService.vk_redirect_uri,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": state,
            "scope": "vkid.personal_info,email",
        }
        auth_url = f"https://id.vk.com/authorize?{urllib.parse.urlencode(params)}"
        return auth_url, code_verifier, code_challenge, state

    @staticmethod
    async def validate_state(state: str):
        """Валидация и удаление state из локального словаря"""
        entry = _state_store.get(state)
        if not entry:
            message = "Неверный или просроченный state токен."
            print(f"ERROR: {message} {state}")  # можно заменить на логгер
            raise ValueError(message)

        # проверка TTL (10 минут)
        if time.time() - entry["ts"] > 600:
            del _state_store[state]
            message = "State токен истёк."
            print(f"ERROR: {message} {state}")
            raise ValueError(message)

        # удаляем после чтения (одноразовый)
        del _state_store[state]
        return entry["data"]


    @staticmethod
    async def get_vk_tokens_2(
        data: dict,
        session: DBSession,
        response: Response,
    ):
        """
        Аутентификация пользователя через VK OAuth
        Args:
            data: Данные пользователя от VK:
                grant_type: Тип авторизации
                code: Код авторизации
                client_id: ID приложения
                client_secret: Секретный код приложения
                redirect_uri: URI перенаправления
                code_verifier: Проверочный код
                device_id: Идентификатор устройства
            session: Сессия базы данных
            response: Объект HTTP ответа
        Returns:
            Токен доступа и тип токена
        """
        auth_url = "https://id.vk.com/oauth2/auth"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=auth_url,
                data=data,
            )
            return response


    @staticmethod
    async def get_vk_tokens(
        session: DBSession,
        response: Response,
        code: str,
        code_verifier: str,
        device_id: str,
    ):
        """Получение токенов VK"""
        try:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": VKOAuthService.client_id,
                "client_secret": VKOAuthService.client_secret,
                "redirect_uri": VKOAuthService.vk_redirect_uri,
                "code_verifier": code_verifier,
                "device_id": device_id,
            }
            async with httpx.AsyncClient() as client:
                # В твоем исходном коде используется AuthService для обмена
                res = await VKOAuthService.get_vk_tokens_2(data, session, response)
                vk_id_token = res.json().get("id_token")
                if not vk_id_token:
                    e = "Не удалось получить id_token от VK."
                    raise HTTPException(status_code=400, detail=e)
                return vk_id_token, res
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Ошибка при получении токенов VK: %s", str(e))
            raise HTTPException(status_code=500, detail="Ошибка обмена токенов")


    @staticmethod
    async def get_vk_user_data(
        data: dict,
        session: DBSession,
        response: Response,
    ):
        user_data_url = "https://id.vk.com/oauth2/user_info"
        async with httpx.AsyncClient() as client:
            user_response = await client.post(
                url=user_data_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            return user_response

    @staticmethod
    async def get_vk_user_info(
            session: DBSession, response: Response, vk_access_token: str
    ):
        """Валидация VK access_token и получение user_id"""

        # TODO Обязательно убрать после тестирования
        logger.debug(f"{vk_access_token=}")

        data = {
            "client_id": VKOAuthService.client_id,
            "access_token": vk_access_token,
        }

        try:
            vk_response = await VKOAuthService.get_vk_user_data(
                data=data,
                session=session,
                response=response,
            )

        except httpx.ConnectError:
            logger.error("VK unreachable")
            raise HTTPException(status_code=502, detail="VK auth provider unreachable")

        except httpx.TimeoutException:
            logger.error("VK timeout")
            raise HTTPException(status_code=504, detail="VK auth timeout")

        logger.info(
            "VK response status=%s body=%s", vk_response.status_code, vk_response.text
        )

        if vk_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid VK access token")

        payload = vk_response.json()

        if "user" not in payload:
            raise HTTPException(status_code=400, detail="VK token validation failed")

        return payload["user"]


    @staticmethod
    async def exchange_codes_for_vk_tokens(
            request: Request,
            session: DBSession,
            response: Response,
            code: str,
            state: str,
            device_id: str,
    ):
        """Финальный шаг: обмен кода на токены и вход"""
        # 1. Валидация state (из Redis)
        stored_data = await VKOAuthService.validate_state(state)

        code_verifier = stored_data["code_verifier"]
        mode = stored_data.get("mode", "login")
        user_id = stored_data.get("user_id")

        # 2. Получение токенов
        vk_id_token, res_obj = await VKOAuthService.get_vk_tokens(
            session, response, code, code_verifier, device_id
        )

        token_data = res_obj.json()

        # 3. Информация о пользователе
        user_info = await VKOAuthService.get_vk_user_info(
            session, response, token_data["access_token"]
        )

        return user_info

        # # 4. Обработка логики (вход или привязка)
        # return await VKOAuthService.handle_oauth_result(
        #     session,
        #     mode,
        #     user_info,
        #     user_id,
        #     token_data["access_token"],
        #     token_data["refresh_token"],
        #     token_data["expires_in"],
        # )



# import base64
# import hashlib
# import secrets
# import time
# import urllib.parse
# import json
#
# import httpx
# from fastapi import HTTPException
# from fastapi.logger import logger
#
# from app.api.deps import DBSession
# from app.core.config import settings
#
# # Локальное хранение state с TTL
# _state_store = {}  # {state: {"data": storage_data, "ts": timestamp}}
#
# class VKOAuthService:
#     """
#     Сервис для работы с VK OAuth 2.0 (Authorization Code Flow + PKCE)
#     """
#
#     # HTTP-клиент для всех запросов к VK
#     _client: httpx.AsyncClient | None = None
#
#     # OAuth конфигурация
#     client_id = settings.VK_OAUTH_CLIENT_ID
#     client_secret = settings.VK_OAUTH_CLIENT_SECRET.get_secret_value()
#     vk_redirect_uri = settings.VK_OAUTH_REDIRECT_URI
#
#     @classmethod
#     async def get_client(cls) -> httpx.AsyncClient:
#         """Возвращает общий AsyncClient"""
#         if cls._client is None:
#             cls._client = httpx.AsyncClient(timeout=10.0)
#         return cls._client
#
#     @classmethod
#     async def close_client(cls):
#         """Закрывает общий AsyncClient"""
#         if cls._client:
#             await cls._client.aclose()
#             cls._client = None
#
#     @staticmethod
#     def generate_pkce_pair() -> tuple[str, str]:
#         """Генерация code_verifier и code_challenge для PKCE"""
#         code_verifier = secrets.token_urlsafe(64)[:128]  # RFC7636: 43-128 chars
#         code_challenge = (
#             base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
#             .decode()
#             .rstrip("=")
#         )
#         return code_verifier, code_challenge
#
#     @staticmethod
#     def set_state(mode: str, user_id: int | None) -> tuple[str, dict]:
#         """
#         Создаёт state + сохраняет данные в локальный словарь с TTL
#         """
#         code_verifier, code_challenge = VKOAuthService.generate_pkce_pair()
#         state = secrets.token_urlsafe(16)
#
#         storage_data = {
#             "code_verifier": code_verifier,
#             "code_challenge": code_challenge,
#             "mode": mode,
#             "user_id": user_id,
#         }
#
#         logger.debug("SET STATE: %s code_verifier=%s code_challenge=%s",
#                      state, storage_data["code_verifier"], storage_data["code_challenge"])
#
#         _state_store[state] = {"data": storage_data, "ts": time.time()}
#         return state, storage_data
#
#     @staticmethod
#     def validate_state(state: str) -> dict:
#         """Проверка и удаление state из локального хранилища"""
#         entry = _state_store.get(state)
#         if not entry:
#             message = "Неверный или просроченный state токен."
#             logger.error("%s %s", message, state)
#             raise HTTPException(status_code=400, detail=message)
#
#         if time.time() - entry["ts"] > 600:  # TTL 10 минут
#             del _state_store[state]
#             message = "State токен истёк."
#             logger.error("%s %s", message, state)
#             raise HTTPException(status_code=400, detail=message)
#
#         del _state_store[state]  # одноразовый
#         return entry["data"]
#
#     @staticmethod
#     def build_auth_url(state: str, code_challenge: str, scope: str = "email") -> str:
#         """Составление URL для перехода на страницу авторизации VK"""
#         params = {
#             "response_type": "code",
#             "client_id": VKOAuthService.client_id,
#             "redirect_uri": VKOAuthService.vk_redirect_uri,
#             "code_challenge": code_challenge,
#             "code_challenge_method": "S256",
#             "state": state,
#             "scope": scope,
#         }
#         return f"https://id.vk.com/authorize?{urllib.parse.urlencode(params)}"
#
#     @classmethod
#     async def exchange_code_for_tokens(
#         cls, code: str, code_verifier: str, device_id: str
#     ) -> dict:
#         """
#         Обмен authorization code на access_token + refresh_token
#         """
#         data = {
#             "grant_type": "authorization_code",
#             "code": code,
#             "client_id": cls.client_id,
#             "client_secret": cls.client_secret,
#             "redirect_uri": cls.vk_redirect_uri,
#             "code_verifier": code_verifier,
#             "device_id": device_id,
#         }
#
#         logger.debug("EXCHANGE CODE REQUEST: code=%s code_verifier=%s", code, code_verifier)
#         client = await cls.get_client()
#         try:
#             response = await client.post("https://oauth.vk.com/access_token", data=data)
#             response.raise_for_status()
#             logger.debug("EXCHANGE CODE RESPONSE: status=%s body=%s", response.status_code, response.text)
#         except httpx.RequestError as e:
#             logger.error("VK request failed: %s", str(e))
#             raise HTTPException(status_code=502, detail="VK auth provider unreachable")
#         except httpx.HTTPStatusError as e:
#             logger.error("VK returned error: %s %s", e.response.status_code, e.response.text)
#             raise HTTPException(status_code=400, detail="Invalid VK code")
#         return response.json()
#
#     @classmethod
#     async def get_user_info(cls, access_token: str) -> dict:
#         """Получение информации о пользователе через VK API"""
#         client = await cls.get_client()
#         data = {"client_id": cls.client_id, "access_token": access_token}
#         try:
#             response = await client.post(
#                 "https://id.vk.com/oauth2/user_info",
#                 data=data,
#                 headers={"Content-Type": "application/x-www-form-urlencoded"},
#             )
#             response.raise_for_status()
#         except httpx.RequestError as e:
#             logger.error("VK request failed: %s", str(e))
#             raise HTTPException(status_code=502, detail="VK auth provider unreachable")
#         except httpx.HTTPStatusError as e:
#             logger.error("VK returned error: %s %s", e.response.status_code, e.response.text)
#             raise HTTPException(status_code=400, detail="Invalid VK access token")
#
#         payload = response.json()
#         if "user" not in payload:
#             raise HTTPException(status_code=400, detail="VK token validation failed")
#         return payload["user"]
#
#     @classmethod
#     async def exchange_and_get_user(
#         cls, code: str, state: str, device_id: str
#     ) -> dict:
#         """
#         Полный флоу: validate_state → exchange_code_for_tokens → get_user_info
#         """
#         stored_data = cls.validate_state(state)
#         code_verifier = stored_data["code_verifier"]
#
#         token_data = await cls.exchange_code_for_tokens(code, code_verifier, device_id)
#         access_token = token_data.get("access_token")
#         if not access_token:
#             raise HTTPException(status_code=400, detail="VK did not return access token")
#
#         user_info = await cls.get_user_info(access_token)
#         return user_info