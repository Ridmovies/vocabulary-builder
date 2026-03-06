from uuid import uuid4

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_words import word_crud
from app.services.stotage import yandex_storage


class WordService:

    @staticmethod
    async def upload_word_image(
        db: AsyncSession,
        word_id: int,
        image: UploadFile,
        user_id: int,
    ):
        # 1. Проверка типа файла
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(status_code=400, detail="Invalid image type")

        # 2. Чтение содержимого файла
        content = await image.read()

        # 3. Генерация уникального имени
        ext = image.filename.split(".")[-1].lower()
        key = f"words/{uuid4()}.{ext}"

        # 4. Загрузка в YandexStorage
        await yandex_storage.upload_file(
            key=key,
            content=content,
            content_type=image.content_type,
            private=False
        )

        # 5. Получение публичного URL
        url = yandex_storage.get_public_url(key)

        word = await word_crud.update_image(
            word_id=word_id,
            db=db,
            image_url=url,
        )
        return word