from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_user import user_crud
from app.models import Category
from app.schemas.user import UserCreate


class UserService:

    @staticmethod
    async def register_user(
        db: AsyncSession,
        obj_in: UserCreate,
    ):
        # 1. создаём пользователя
        user = await user_crud.create(db=db, obj_in=obj_in)

        # 2. создаём дефолтную категорию
        default_category = Category(
            name="default",
            description="Категория по умолчанию",
            owner_id=user.id,
        )
        db.add(default_category)

        await db.commit()      # один коммит
        await db.refresh(user)

        return user