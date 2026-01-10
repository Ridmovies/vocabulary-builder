from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user import UserCreate
from app.utils.pwd import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserCreate]):
    """CRUD операции для пользователей."""

    async def get_by_email(
        self,
        db: AsyncSession,
        *,
        email: str
    ) -> Optional[User]:
        """Получить пользователя по email"""
        query = select(User).where(
            User.email == email
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create(
            self,
            db: AsyncSession,
            *,
            obj_in: UserCreate
    ) -> User:
        """Создать пользователя с хешированным паролем."""
        # Хешируем пароль
        hashed_password = get_password_hash(obj_in.password)

        # Создаем объект пользователя
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=hashed_password
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def authenticate(
            self,
            db: AsyncSession,
            *,
            email: str,
            password: str
    ) -> Optional[User]:
        """Аутентификация пользователя."""

        # Находим пользователя
        user = await self.get_by_email(
            db,
            email=email
        )

        if not user:
            return None

        # Проверяем пароль
        if not verify_password(password, user.hashed_password):
            return None

        # Проверяем активность
        if not user.is_active:
            return None

        return user


# Экземпляр для использования
user_crud = CRUDUser(User)