from abc import ABC, abstractmethod
from tempfile import SpooledTemporaryFile
from typing import BinaryIO

from fastapi import UploadFile


class IMediaRepository(ABC):
    """Repository interface for media file operations."""

    @abstractmethod
    def upload(
        self,
        file: str | UploadFile | BinaryIO | SpooledTemporaryFile,
        key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Uploads a file to S3-compatible storage.

        :param file: File path, UploadFile, or binary stream
        :param key: Target file name (e.g., "avatars/user123.png")
        :param content_type: MIME type (e.g., "image/png")
        :return: The generated key in S3
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Deletes a file from S3.

        :param key: The S3 key to delete
        """
        raise NotImplementedError

    @abstractmethod
    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generates a presigned download URL for a file.

        :param key: S3 key to generate the URL for
        :param expires_in: URL expiry time in seconds (default: 1 hour)
        :return: A presigned URL
        """
        raise NotImplementedError
