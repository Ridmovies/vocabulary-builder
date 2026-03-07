import io
from abc import ABC, abstractmethod
from urllib.parse import urlparse

from botocore.config import Config

import boto3

from app.core.config import settings


class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, key: str, content: bytes, content_type: str) -> None:
        ...

    @abstractmethod
    async def delete_file(self, key: str) -> None:
        ...

    @abstractmethod
    def get_public_url(self, key: str) -> str:
        ...

    @abstractmethod
    def generate_presigned_url(self, key: str, expires: int = 300) -> str:
        ...


class YandexStorage(StorageService):
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.YANDEX_CLOUD_ENDPOINT,
            aws_access_key_id=settings.YANDEX_CLOUD_ACCESS_KEY.get_secret_value(),
            aws_secret_access_key=settings.YANDEX_CLOUD_SECRET_KEY.get_secret_value(),
            region_name="ru-central1",
            config=Config(signature_version="s3v4"),
        )
        self._public_bucket = settings.YANDEX_CLOUD_PUBLIC_BUCKET_NAME
        self._public_base_url = f"https://storage.yandexcloud.net/{self._public_bucket}"

    async def upload_file(
        self,
        key: str,
        content: bytes,
        content_type: str,
        private: bool = False,
    ) -> None:
        bucket = self._public_bucket
        self._client.upload_fileobj(
            io.BytesIO(content),
            bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )

    async def delete_file(self, key: str, private: bool = False) -> None:
        bucket = self._public_bucket
        self._client.delete_object(Bucket=bucket, Key=key)

    def get_public_url(self, key: str) -> str:
        # возвращаем публичный URL всегда через публичный бакет
        return f"{self._public_base_url}/{key}"


    def generate_presigned_url(
        self, key: str, expires: int = settings.YANDEX_PRESIGNED_URL_EXPIRES_SECONDS
    ) -> str:
        pass
        # return self._client.generate_presigned_url(
        #     "get_object",
        #     Params={
        #         "Bucket": self._private_bucket,
        #         "Key": key,
        #         "ResponseContentDisposition": "inline",
        #     },
        #     ExpiresIn=expires,
        # )

    @staticmethod
    def extract_key(url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")
        parts = path.split("/", 1)
        return parts[1] if len(parts) > 1 else ""

yandex_storage = YandexStorage()
