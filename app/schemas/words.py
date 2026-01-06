from pydantic import BaseModel, Field


class WordBase(BaseModel):
    """Базовая схема слова."""
    english: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Слово на английском языке",
        examples=["hello"]
    )
    russian: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Перевод на русский язык",
        examples=["привет"]
    )


class WordCreate(WordBase):
    """Схема для создания нового слова."""
    pass  # Наследуем все поля от WordBase


class WordUpdate(BaseModel):
    """Схема для обновления слова (все поля опциональны)."""
    english: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Слово на английском языке",
        examples=["hello"]
    )
    russian: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Перевод на русский язык",
        examples=["привет"]
    )