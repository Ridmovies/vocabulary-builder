# app/models/__init__.py
from app.models.base import Base
from app.models.word import Word
from app.models.user import User
from app.models.category import Category, word_category

# Импортируем таблицу связи (важно для Alembic!)

# Список всех моделей для Alembic
__all__ = ["Base", "Word", "Category", "word_category", "User"]