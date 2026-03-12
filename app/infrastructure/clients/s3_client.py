import os
from io import IOBase
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, Callable
from uuid import uuid4

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile
from loguru import logger

from app.config import config
from app.infrastructure.clients.media_client_protocol import MediaClientProtocol


class S3Client(MediaClientProtocol):
    """Real S3 client implementation."""

    def __init__(self):
        region = config.AWS_DEFAULT_REGION

        self.client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=f"https://s3.{region}.amazonaws.com",
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"},
            ),
        )

        self.bucket = config.AWS_S3_MEDIA_BUCKET
        self.aws_s3_root_folder = config.AWS_S3_MEDIA_ROOT_FOLDER

    def get_unique_link(self, key: str) -> str:
        """Generate a unique S3 key with UUID."""
        name, extension = os.path.splitext(key)
        return f"{self.aws_s3_root_folder}/{name}_{uuid4()}{extension}"

    def upload_file(
        self,
        key: str,
        file: str | UploadFile | BinaryIO | SpooledTemporaryFile,
        callback: Callable = None,
        extra: dict = None,
        use_multipart_upload: bool = True,
    ) -> str:
        try:
            conf = {}

            key = self.get_unique_link(key)
            extra = extra or {}

            if use_multipart_upload:
                conf["Config"] = TransferConfig(
                    multipart_threshold=1024 * 1024 * 25,  # 25MB
                    multipart_chunksize=1024 * 1024 * 25,
                    max_concurrency=2,
                )

            if isinstance(file, str):
                if not os.path.isfile(file):
                    raise FileNotFoundError(f"File {file} does not exist!")
                with open(file, "rb") as data:
                    self.client.upload_fileobj(
                        Fileobj=data,
                        Bucket=self.bucket,
                        Key=key,
                        Callback=callback,
                        ExtraArgs=extra,
                        **conf,
                    )
            elif isinstance(file, UploadFile):
                self.client.upload_fileobj(
                    Fileobj=file.file,
                    Bucket=self.bucket,
                    Key=key,
                    Callback=callback,
                    ExtraArgs=extra,
                    **conf,
                )
            elif isinstance(file, (IOBase, SpooledTemporaryFile)):
                self.client.upload_fileobj(
                    Fileobj=file,
                    Bucket=self.bucket,
                    Key=key,
                    Callback=callback,
                    ExtraArgs=extra,
                    **conf,
                )
            else:
                raise TypeError("Unsupported file type for upload.")

            logger.info(f"File uploaded to S3: {key}")
            return key
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def delete_file(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted file from S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
