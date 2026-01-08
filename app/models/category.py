from sqlalchemy import String, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Category(Base):
    """
    Модель категории для слов.
    Связь многие-ко-многим с Word.
    """
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(50)
    )

    description: Mapped[str | None] = mapped_column(
        String(100)
    )

    # Связи
    words: Mapped[list["Word"]] = relationship(
        "Word",
        secondary="word_categories",  # Таблица связи
        back_populates="categories",
        lazy="selectin"  # Загружаем категории при запросе слов
    )


# Таблица связи многие-ко-многим между Word и Category
word_category = Table(
    "word_categories",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("word_id", Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False),

    # Уникальное ограничение: нельзя добавить одну пару дважды
    # UniqueConstraint("word_id", "category_id", name="uq_word_category"),
)