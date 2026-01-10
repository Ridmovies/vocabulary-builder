from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user import UserCreate
from app.utils.pwd import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserCreate]):
    """CRUD операции для пользователей."""

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


# Экземпляр для использования
user_crud = CRUDUser(User)