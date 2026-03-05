from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_words import word_crud


class WordService:

    @staticmethod
    async def upload_word_image(
        db: AsyncSession,
        word_id: int,
        image: UploadFile,
        user_id: int,
    ):
        # 1. проверка типа
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise ValueError("Invalid image type")

        # 2. генерация имени
        filename = f"{uuid4()}.jpg"

        # # 3. загрузка в CDN
        # url = await image_storage_service.upload_file(
        #     file=image,
        #     path=f"words/{filename}"
        # )

        image_url = "https://medium.com" + "/" + filename

        # 4. обновление слова
        return await word_crud.update_image(
            db=db,
            word_id=word_id,
            image_url=image_url,
        )