# app/core/security.py
import secrets
from datetime import timedelta, datetime, timezone
from typing import Optional, Dict, Any

import jwt
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


def create_jwt_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
) -> str:
    """
    Создать JWT токен.

    Args:
        data: Данные для payload
        expires_delta: Время жизни токена
        token_type: Тип токена (access/refresh)

    Returns:
        Закодированный JWT токен
    """
    to_encode = data.copy()

    # Время истечения
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == "access":
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        else:  # refresh
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

    # Данные токена
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": token_type,
        "jti": secrets.token_urlsafe(16)  # Уникальный ID токена
    })

    # Кодируем
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Декодировать JWT токен.

    Returns:
        Payload токена или None при ошибке
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None


# Утилиты для работы с куками
def set_auth_cookies(
        response: Response,
        access_token: str,
        refresh_token: Optional[str] = None,
        csrf_token: Optional[str] = None
) -> None:
    """
    Установить аутентификационные куки.

    Args:
        response: FastAPI Response объект
        access_token: Access JWT токен
        refresh_token: Refresh JWT токен (опционально)
        csrf_token: CSRF токен (опционально)
    """
    # Access токен кука
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=settings.ACCESS_TOKEN_COOKIE_PATH,
        domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN,
        secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
        httponly=settings.ACCESS_TOKEN_COOKIE_HTTPONLY,
        samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
    )

    # Refresh токен кука (если есть)
    if refresh_token:
        response.set_cookie(
            key=settings.REFRESH_TOKEN_COOKIE_NAME,
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/api/auth",  # Только для эндпоинтов refresh
            secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
            httponly=True,
            samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
        )

    # CSRF токен кука (если есть)
    if csrf_token:
        response.set_cookie(
            key=settings.CSRF_TOKEN_COOKIE_NAME,
            value=csrf_token,
            max_age=30 * 24 * 60 * 60,  # 30 дней
            path="/",
            secure=settings.ACCESS_TOKEN_COOKIE_SECURE,
            httponly=False,  # Должен быть доступен JS для отправки в заголовках
            samesite=settings.ACCESS_TOKEN_COOKIE_SAMESITE
        )


def get_token_from_cookie(request: Request, token_type: str = "access") -> Optional[str]:
    """
    Получить токен из куки.

    Args:
        request: FastAPI Request
        token_type: Тип токена (access/refresh/csrf)

    Returns:
        Токен или None
    """
    cookie_name = {
        "access": settings.ACCESS_TOKEN_COOKIE_NAME,
        "refresh": settings.REFRESH_TOKEN_COOKIE_NAME,
        "csrf": settings.CSRF_TOKEN_COOKIE_NAME
    }.get(token_type)

    if not cookie_name:
        return None

    return request.cookies.get(cookie_name)


def clear_auth_cookies(response: Response) -> None:
    """Очистить аутентификационные куки."""
    cookies_to_clear = [
        settings.ACCESS_TOKEN_COOKIE_NAME,
        settings.REFRESH_TOKEN_COOKIE_NAME,
        settings.CSRF_TOKEN_COOKIE_NAME
    ]

    for cookie_name in cookies_to_clear:
        response.delete_cookie(
            key=cookie_name,
            path="/",
            domain=settings.ACCESS_TOKEN_COOKIE_DOMAIN
        )


def create_access_token(user_id: int, username: str, email: str) -> str:
    """Создать access токен."""
    return create_jwt_token(
        data={
            "sub": str(user_id),
            "username": username,
            "email": email
        },
        token_type="access"
    )


def create_refresh_token(user_id: int) -> str:
    """Создать refresh токен."""
    return create_jwt_token(
        data={"sub": str(user_id)},
        token_type="refresh"
    )


def create_csrf_token() -> str:
    """Создать CSRF токен."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(csrf_token: str, csrf_cookie: str) -> bool:
    """
    Проверить CSRF токен.

    Args:
        csrf_token: Токен из заголовка X-CSRF-Token
        csrf_cookie: Токен из куки

    Returns:
        True если токены совпадают
    """
    return secrets.compare_digest(csrf_token, csrf_cookie)

