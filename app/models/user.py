from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    # Основные поля
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[bytes] = mapped_column(BYTEA)

    # Активность
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    favorite_words: Mapped[list["Word"]] = relationship(
        "Word",
        secondary="favorite_words",
        lazy="selectin",
        back_populates="favorited_by",
    )

    # Отношение "один-ко-многим" с моделью OAuthAccount
    # Один пользователь может иметь несколько связанных OAuth-аккаунтов
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",  # Удалять OAuth-аккаунты при удалении пользователя
    )