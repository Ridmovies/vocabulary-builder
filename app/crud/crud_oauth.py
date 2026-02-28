from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import OAuthAccount
from app.schemas.oauth import OAuthAccountCreate


class OAuthAccountRepository:
    model = OAuthAccount  # Указываем модель SQLAlchemy для работы

    @staticmethod
    async def get_by_provider_and_account_id(
        session: AsyncSession, provider: str, account_id: str
    ) -> OAuthAccount | None:
        """
        Находит OAuthAccount по провайдеру и account_id.
        Возвращает объект OAuthAccount с привязанным пользователем или None.
        """
        result = await session.execute(
            select(OAuthAccount)
            .where(
                OAuthAccount.oauth_name == provider,
                OAuthAccount.account_id == account_id,
            )
            .options(
                selectinload(OAuthAccount.user)
            )  # чтобы сразу загрузить связанного User
        )
        return result.scalars().first()

    @staticmethod
    async def create(
            db: AsyncSession,
            obj_in: OAuthAccountCreate
    ) -> OAuthAccount:
        """
        Создать новый объект.

        Args:
            db: Сессия базы данных
            obj_in: Pydantic схема с данными

        Returns:
            Созданный объект
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = OAuthAccount(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj