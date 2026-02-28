from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class OAuthAccount(Base):
    """Базовая таблица SQLAlchemy для хранения данных OAuth-аккаунта."""

    __tablename__ = "oauth_account"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="cascade"),
        nullable=False,  # OAuth-аккаунт должен быть связан с пользователем
        # index=True # Для производительности поиска по user_id
    )
    # Название провайдера OAuth (например, "google", "vk")
    oauth_name: Mapped[str] = mapped_column(
        String(length=100), index=True, nullable=False
    )
    # account_id: ID пользователя у провайдера (например, уникальный ID Google или VK)
    account_id: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=False
    )
    # account_email: Email пользователя, полученный от провайдера
    account_email: Mapped[str | None]

    # Отношение "многие-к-одному" с моделью User
    user: Mapped["User"] = relationship(back_populates="oauth_accounts")