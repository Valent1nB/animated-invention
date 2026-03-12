from tempfile import SpooledTemporaryFile
from typing import BinaryIO, Callable

from fastapi import UploadFile
from loguru import logger

from app.infrastructure.clients.media_client_protocol import MediaClientProtocol


class S3ClientMock(MediaClientProtocol):
    """Mock S3 client for testing and local development."""

    def upload_file(
        self,
        key: str,
        file: str | UploadFile | BinaryIO | SpooledTemporaryFile,
        callback: Callable | None = None,
        extra: dict | None = None,
        use_multipart_upload: bool = True,
    ) -> str:
        logger.info(f"[MOCK] Uploaded file to mock storage: {key}")
        return f"mock/{key}"

    def delete_file(self, key: str) -> None:
        logger.info(f"[MOCK] Deleted file from mock storage: {key}")

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        logger.info(f"[MOCK] Generated presigned URL for {key}")
        return f"https://mock-bucket.s3.amazonaws.com/{key}?expires_in={expires_in}"
