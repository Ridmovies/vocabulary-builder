from typing import Optional, List

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


class WordRead(WordBase):
    id: int = Field(
        ...,
        description="id слова",
        examples=["1"]
    )

    # category_ids: Optional[List[int]] = Field(
    #     default_factory=list,
    #     description="ID категорий для слова"
    # )


class WordCreate(WordBase):
    """Схема для создания слова с категориями."""
    category_ids: Optional[list[int]] = Field(
        None,
        description="Список ID категорий для слова"
    )


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

    # category_ids: Optional[list[int]] = Field(
    #     None,
    #     description="Список ID категорий для слова"
    # )