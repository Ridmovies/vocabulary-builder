from googletrans import Translator
from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DBSession, UserDep

router = APIRouter()


class WordRequest(BaseModel):
    word: str


class TranslationResponse(BaseModel):
    original: str
    translated: str
    src_lang: str
    dest_lang: str



@router.post("", response_model=TranslationResponse)
async def translate(
        session: DBSession,
        current_user: UserDep,
        request: WordRequest,
):
    # Переводим слово с английского на русский
    translator = Translator()
    # Ждём выполнение корутины
    result = await translator.translate(request.word, src='ru', dest='en')

    # Возвращаем только сериализуемые поля
    return TranslationResponse(
        original=result.origin,
        translated=result.text,
        src_lang=result.src,
        dest_lang=result.dest
    )