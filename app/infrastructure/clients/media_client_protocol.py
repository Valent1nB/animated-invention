from tempfile import SpooledTemporaryFile
from typing import BinaryIO, Callable, Protocol

from fastapi import UploadFile


class MediaClientProtocol(Protocol):
    """Protocol for S3-compatible media storage clients."""

    def upload_file(
        self,
        key: str,
        file: str | UploadFile | BinaryIO | SpooledTemporaryFile,
        callback: Callable | None = None,
        extra: dict | None = None,
        use_multipart_upload: bool = True,
    ) -> str:
        """Upload a file to S3 and return the object key."""
        ...

    def delete_file(self, key: str) -> None:
        """Delete a file from S3 by key."""
        ...

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned download URL for an S3 object."""
        ...
