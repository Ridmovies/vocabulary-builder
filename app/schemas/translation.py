from enum import Enum

from pydantic import BaseModel, Field


class LangEnum(str, Enum):
    en = "en"
    ru = "ru"

class WordRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    src_lang: LangEnum = Field(
        default=LangEnum.en,
        description="Исходный язык",
        examples=[LangEnum.en, LangEnum.ru]
    )
    dest_lang: LangEnum = Field(
        default=LangEnum.ru,
        description="Язык перевода",
        examples=[LangEnum.ru, LangEnum.en]
    )


class TranslationResponse(BaseModel):
    original: str
    translated: str
    src_lang: str
    dest_lang: str
    all_translations: list[list] | None = None