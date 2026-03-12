from enum import StrEnum

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(StrEnum):
    test = "test"
    local = "local"
    dev = "dev"
    prod = "prod"


class Config(BaseSettings):
    ENV: Env = Env.local

    PGHOST: str = "postgres"
    PGPORT: int = 5432
    PGPASSWORD: str | None = None
    POSTGRES_DB: str = "px"
    POSTGRES_USER: str = "postgres"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.PGPASSWORD}"
            f"@{self.PGHOST}:{self.PGPORT}/{self.POSTGRES_DB}"
        )

    AUTH_SIGNATURE_SECRET: str = ""
    JWT_ACCESS_LIFETIME: int = 3600
    JWT_REFRESH_LIFETIME: int = 604800
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""

    FRONTEND_REDIRECT_URI: str = "http://localhost:3000/example"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/example"
    STATE_TOKEN_AUDIENCE: str = "fastapi-users:oauth-state"

    # AWS S3 Configuration
    AWS_DEFAULT_REGION: str = "eu-central-1"
    AWS_S3_MEDIA_BUCKET: str = ""
    AWS_S3_MEDIA_ROOT_FOLDER: str = "media"

    # Media upload configuration
    SUPPORTED_MEDIA_FORMATS: list[str] = ["jpg", "jpeg", "png", "gif", "webp", "pdf", "doc", "docx"]
    MAX_UPLOAD_MEDIA_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Config()
