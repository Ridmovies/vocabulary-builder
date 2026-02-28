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
    async def get_vk_auth_url():
        """Установка параметров авторизации и сохранение их в Redis"""
        code_verifier, code_challenge = VKOAuthService.generate_pkce_pair()
        state = secrets.token_urlsafe(16)

        storage_data = {
            "code_verifier": code_verifier,
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
        return auth_url

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
    async def get_vk_tokens(
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

            # res = await VKOAuthService.get_vk_tokens_2(data, session, response)
            auth_url = "https://id.vk.com/oauth2/auth"
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    url=auth_url,
                    data=data,
                )

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
            vk_access_token: str
    ):
        """Валидация VK access_token и получение user_id"""
        data = {
            "client_id": VKOAuthService.client_id,
            "access_token": vk_access_token,
        }
        try:
            vk_response = await VKOAuthService.get_vk_user_data(
                data=data,
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
            session: DBSession,
            code: str,
            state: str,
            device_id: str,
    ):
        """Финальный шаг: обмен кода на токены и вход"""
        # 1. Валидация state (из Redis)
        stored_data = await VKOAuthService.validate_state(state)

        code_verifier = stored_data["code_verifier"]

        # 2. Получение токенов
        vk_id_token, res_obj = await VKOAuthService.get_vk_tokens(
            code=code, code_verifier=code_verifier, device_id=device_id
        )

        token_data = res_obj.json()

        # 3. Информация о пользователе
        user_info = await VKOAuthService.get_vk_user_info(
            vk_access_token=token_data["access_token"]
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