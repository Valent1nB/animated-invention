import os
from tempfile import SpooledTemporaryFile
from typing import BinaryIO

from fastapi import UploadFile

from app.config import Env, config
from app.domain.repositories.media_repository import IMediaRepository
from app.infrastructure.clients.media_client_protocol import MediaClientProtocol
from app.infrastructure.clients.s3_client import S3Client
from app.infrastructure.clients.s3_client_mock import S3ClientMock


class MediaRepository(IMediaRepository):
    def __init__(self, client: MediaClientProtocol):
        self.client = client

    def _get_file_size(self, file: str | UploadFile | BinaryIO | SpooledTemporaryFile) -> int:
        if isinstance(file, str):
            return os.path.getsize(file)

        stream = file.file if isinstance(file, UploadFile) else file
        if hasattr(stream, "seek") and hasattr(stream, "tell"):
            current_pos = stream.tell()
            stream.seek(0, os.SEEK_END)
            size = stream.tell()
            stream.seek(current_pos)
            return size

        raise TypeError("Unsupported file type for size check.")

    def validate_file_format(self, key: str, file: str | UploadFile | BinaryIO | SpooledTemporaryFile) -> None:
        _, ext = os.path.splitext(key)
        if not ext:
            raise ValueError(f"No file extension found in '{key}'")
        ext = ext.lstrip(".").lower()
        if ext not in config.SUPPORTED_MEDIA_FORMATS:
            raise ValueError(f"Unsupported media format: '{ext}'. Supported formats: {config.SUPPORTED_MEDIA_FORMATS}")

        size = self._get_file_size(file)
        if size > config.MAX_UPLOAD_MEDIA_FILE_SIZE:
            raise ValueError("Uploaded file is too large")

    def upload(
        self,
        file: str | UploadFile | BinaryIO | SpooledTemporaryFile,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        self.validate_file_format(key, file)
        extra = {"ContentType": content_type}
        return self.client.upload_file(key, file, extra=extra)

    def delete(self, key: str) -> None:
        self.client.delete_file(key)

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(key, expires_in)


def get_media_repo() -> IMediaRepository:
    if config.ENV in (Env.local, Env.test):
        return MediaRepository(S3ClientMock())
    return MediaRepository(S3Client())


media_repo = get_media_repo()
