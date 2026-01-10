from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Word(Base):
    """
    Модель слова для изучения английского языка.

    Эта модель представляет таблицу 'words' в базе данных PostgreSQL.
    Каждая строка в таблице - одно слово для изучения.

    """

    # Имя таблицы в базе данных
    # SQLAlchemy автоматически создаст таблицу с этим именем
    __tablename__ = "words"

    # ОСНОВНЫЕ ПОЛЯ СЛОВА
    # ===================

    # Английское слово (обязательное поле)
    # String(100) - строка максимум 100 символов
    english: Mapped[str] = mapped_column(
        String(100),
        nullable=False,  # Не может быть пустым
        index=True,  # Создаст индекс для быстрого поиска
        comment="Слово на английском языке"
    )

    # Русский перевод (обязательное поле)
    russian: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Перевод на русский язык"
    )

    # Владелец слова
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    owner: Mapped["User"] = relationship("User")

    # ДОБАВЛЯЕМ связь с категориями:
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary="word_categories",  # Таблица связи
        back_populates="words",
        lazy="selectin",  # Загружаем категории при запросе
        # cascade="all, delete"  # Удалить связи при удалении слова
    )

    favorited_by: Mapped[list["User"]] = relationship(
        "User",
        secondary="favorite_words",
        lazy="selectin",
        back_populates="favorite_words",
    )