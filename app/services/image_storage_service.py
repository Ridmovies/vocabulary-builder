from uuid import uuid4

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.crud.crud_words import word_crud
from app.services.stotage import yandex_storage, YandexStorage


class WordService:

    @staticmethod
    async def upload_word_image(
        db: AsyncSession,
        word_id: int,
        image: UploadFile,
        user_id: int,
    ):
        # сначала проверка прав
        await word_crud.get_for_user(
            db=db,
            word_id=word_id,
            user_id=user_id,
        )

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
        await db.commit()
        return word

    @staticmethod
    async def delete_word_image(
        db: AsyncSession,
        word_id: int,
        user_id: int,
    ):

        # сначала проверка прав
        word = await word_crud.get_for_user(
            db=db,
            word_id=word_id,
            user_id=user_id,
        )

        logger.debug(f"{word.image_url=}")

        if word.image_url:

            key = YandexStorage.extract_key(url=word.image_url)
            logger.debug(f"{key=}")

            await yandex_storage.delete_file(
                key=key,
                private=False
            )

        word.image_url = None
        await db.commit()

        return word



