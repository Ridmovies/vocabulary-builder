import base64
import hashlib
import secrets
import time
import urllib.parse
from uuid import uuid4

import httpx

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.api.deps import DBSession
from app.core.config import settings
from app.core.logger import logger
from app.core.security import create_access_token, create_refresh_token, create_csrf_token, set_auth_cookies
from app.crud.crud_oauth import OAuthAccountRepository
from app.crud.crud_user import user_crud
from app.models import User
from app.schemas.oauth import OAuthAccountCreate
from app.utils.pwd import get_password_hash

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
        """
        Генерация пары PKCE (Proof Key for Code Exchange).
        PKCE добавляет криптографическое доказательство того, что тот,
        кто обменивает authorization code на access_token, — тот же субъект, который инициировал авторизацию.
        Это защита от перехвата кода (authorization code interception attack).
        """
        # code_verifier — криптографически случайная строка высокой энтропии (43–128 символов по стандарту RFC 7636).
        # В коде используется secrets.token_urlsafe(64) — это генерация криптостойкой строки.
        # Обрезка до 128 символов гарантирует соответствие верхнему лимиту.
        code_verifier = secrets.token_urlsafe(64)[:128]
        # code_challenge — это публичное криптографическое обязательство (commitment) к будущему code_verifier.
        code_challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )
        return code_verifier, code_challenge

    @staticmethod
    async def get_vk_auth_url():
        """Установка параметров авторизации"""
        code_verifier, code_challenge = VKOAuthService.generate_pkce_pair()
        # state Это случайный идентификатор сессии авторизации
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
            logger.debug(f"ERROR: {message} {state}")  # можно заменить на логгер
            raise ValueError(message)

        # проверка TTL (10 минут)
        if time.time() - entry["ts"] > 600:
            del _state_store[state]
            message = "State токен истёк."
            logger.debug(f"ERROR: {message} {state}")
            raise ValueError(message)

        # удаляем после чтения (одноразовый)
        del _state_store[state]
        return entry["data"]


    @staticmethod
    async def get_vk_access_token(
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
                return res
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Ошибка при получении токенов VK: %s", str(e))
            raise HTTPException(status_code=500, detail="Ошибка обмена токенов")


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

            auth_url = "https://id.vk.com/oauth2/auth"
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    url=auth_url,
                    data=data,
                )
                # Содержит идентификационные данные пользователя (sub = VK user_id).
                # это криптографически подписанное доказательство личности пользователя, которое backend может использовать, не обращаясь к VK API напрямую.
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

        logger.debug(
            "VK response status=%s body=%s", vk_response.status_code, vk_response.text
        )

        if vk_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid VK access token")

        payload = vk_response.json()

        if "user" not in payload:
            raise HTTPException(status_code=400, detail="VK token validation failed")

        return payload["user"]


    @staticmethod
    async def register_or_login_vk(
            session: DBSession,
            vk_access_token: str,
    ):
        """
        """

        # Получаем user_info
        user_info = await VKOAuthService.get_vk_user_info(
            vk_access_token=vk_access_token,
        )
        # Подготавливаем данные
        vk_id = user_info.get("user_id")
        # Если email — обязательный бизнес-инвариант, единственная корректная модель — двухфазная регистрация
        email = user_info.get("email")

        if not email:
            # TODO Hardcode email!!! Email don't use in app. It's fine.
            hash_digest = hashlib.sha256(vk_id.encode()).hexdigest()[
                :12
            ]  # первые 12 символов
            email = f"user_{hash_digest}@temp.local"

        # TODO Hardcode username
        username = f"user_{uuid4().hex[:10]}"

        # first_name = user_info.get("first_name")
        # last_name = user_info.get("last_name")
        # birthday = user_info.get("birthday")
        # gender = user_info.get("sex")
        # avatar = user_info.get("avatar")

        # Генерировать криптографически случайную строку, хешировать и сохранять.
        # Пользователь не знает этот пароль.
        # Если позже понадобится обычный вход — реализуется отдельный флоу «установить пароль».
        password = secrets.token_urlsafe(32)
        # Хешируем пароль перед сохранением в БД
        hashed_password = get_password_hash(password)


        # Ищем oauth_account по vk_id
        oauth_account = await OAuthAccountRepository.get_by_provider_and_account_id(
            session=session, provider="vk", account_id=vk_id
        )

        # Если oauth_account найден, получаем пользователя
        if oauth_account:
            user = oauth_account.user
            logger.debug("oauth_account найден, получаю пользователя")
        else:
            # Или получаем пользователя по емайл
            user = await user_crud.get_by_email(db=session, email=email)

            if user:
                # Привязываем VK к существующему аккаунту
                logger.debug("Привязываем VK к существующему аккаунту")
                await VKOAuthService.create_vk_oauth_account(
                    session=session,
                    user_id=user.id,
                    user_info=user_info,
                )

        if not user:
            # Если пользователя нет, то регистрируем

            user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                is_verified=True,  # ← сразу помечаем как подтвержденного
            )

            session.add(user)
            await session.commit()

            await VKOAuthService.create_vk_oauth_account(
                session=session,
                user_id=user.id,
                user_info=user_info,
            )

        access_token: str = create_access_token(
            user_id=int(user.id),
            username=user.username,
            email=user.email,
        )

        refresh_token = create_refresh_token(user_id=int(user.id))

        # 3. Создаем CSRF токен
        csrf_token = create_csrf_token()

        return {"access_token": access_token, "refresh_token": refresh_token, "csrf_token": csrf_token}


    @staticmethod
    async def get_access_token_from_code(
            code: str,
            state: str,
            device_id: str
    ) -> str:
        """Финальный шаг: обмен кода на токены и вход"""
        # 1. Валидация state
        stored_data = await VKOAuthService.validate_state(state)

        code_verifier = stored_data["code_verifier"]

        # 2. Получение токенов
        vk_id_token, res_obj = await VKOAuthService.get_vk_tokens(
            code=code, code_verifier=code_verifier, device_id=device_id
        )
        logger.debug(f"{vk_id_token=}")
        token_data = res_obj.json()
        logger.debug(f"{token_data=}")
        vk_access_token = token_data["access_token"]
        return vk_access_token


    # @staticmethod
    # async def exchange_codes_for_vk_tokens(
    #         session: DBSession,
    #         code: str,
    #         state: str,
    #         device_id: str,
    # ):
    #     """Финальный шаг: обмен кода на токены и вход"""
    #     # 1. Валидация state (из Redis)
    #     stored_data = await VKOAuthService.validate_state(state)
    #
    #     code_verifier = stored_data["code_verifier"]
    #
    #     # 2. Получение токенов
    #     vk_id_token, res_obj = await VKOAuthService.get_vk_tokens(
    #         code=code, code_verifier=code_verifier, device_id=device_id
    #     )
    #
    #     token_data = res_obj.json()
    #
    #     # 3. Информация о пользователе
    #     user_info = await VKOAuthService.get_vk_user_info(
    #         vk_access_token=token_data["access_token"]
    #     )
    #
    #     return {
    #         "user_info": user_info,
    #         "vk_access_token": token_data["access_token"],
    #     }


    @staticmethod
    async def create_vk_oauth_account(
        session: AsyncSession,
        user_id: int,
        user_info: dict,
    ):
        logger.debug("Получаем или создаем пользователя VK.")
        vk_id = user_info.get("user_id")
        email = user_info.get("email")
        logger.debug(f"user_info: {user_info}")
        logger.debug(f"Получаем или создаем пользователя VK с vk_id: {vk_id}")
        logger.debug(f"Получаем или создаем пользователя VK с email: {email}")

        # Создание экземпляра Pydantic-модели OAuthAccountCreate
        oauth_data = OAuthAccountCreate(
            oauth_name="vk",
            account_id=vk_id,
            user_id=user_id,
            account_email=email,
        )
        # Передаём Pydantic-модель в метод create репозитория
        oauth_account = await OAuthAccountRepository.create(
            db=session, obj_in=oauth_data
        )
        logger.debug(f"Аккаунт OAuth VK успешно создан: {oauth_account}")
