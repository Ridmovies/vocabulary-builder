# app/models/base.py

from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


# 3. СОЗДАЕМ БАЗОВЫЙ КЛАСС ДЛЯ МОДЕЛЕЙ
# =====================================
# DeclarativeBase - это основа для всех наших таблиц (моделей)

# Что это дает:
# 1. Все наши модели (таблицы) будут наследоваться от этого класса
# 2. SQLAlchemy автоматически поймет, что это таблицы БД


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Содержит общие поля и настройки для всех таблиц.
    """

    # Общие поля для всех моделей
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,  # Создаст индекс для быстрого поиска
        autoincrement=True  # Автоматическая генерация ID
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # Храним с часовым поясом
        server_default=func.now(),  # По умолчанию - текущее время
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Автоматически обновляется при изменении записи
        nullable=False
    )

    def __repr__(self) -> str:
        """Строковое представление объекта для отладки."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Конвертирует модель в словарь.

        Пример использования:
        >>> word = Word(english="hello", russian="привет")
        >>> word.to_dict()
        {'id': None, 'english': 'hello', 'russian': 'привет', ...}
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }