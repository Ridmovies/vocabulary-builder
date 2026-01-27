from googletrans import Translator
from fastapi import APIRouter

from app.api.deps import DBSession, UserDep
from app.schemas.translation import TranslationResponse, WordRequest

router = APIRouter()


@router.post("", response_model=TranslationResponse)
async def translate(
        session: DBSession,
        current_user: UserDep,
        request: WordRequest,
):
    # Переводим слово с английского на русский
    translator = Translator()
    # Ждём выполнение корутины
    result = await translator.translate(request.word, src=request.src_lang, dest=request.dest_lang)


    # Возвращаем только сериализуемые поля
    return TranslationResponse(
        original=result.origin,
        translated=result.text,
        all_translations=result.extra_data.get("all-translations", []),
        src_lang=result.src,
        dest_lang=result.dest
    )