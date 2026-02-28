# app/models/__init__.py
from app.models.base import Base
from app.models.oauth_account import OAuthAccount
from app.models.word import Word
from app.models.user import User
from app.models.category import Category, word_category
from app.models.favorite_words import favorite_words

# Импортируем таблицу связи (важно для Alembic!)

# Список всех моделей для Alembic
__all__ = ["Base", "Word", "Category", "word_category", "User", "favorite_words", "OAuthAccount"]