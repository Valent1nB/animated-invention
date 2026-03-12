from typing import Annotated

from fastapi import Depends

from app.domain.repositories.media_repository import IMediaRepository
from app.infrastructure.repositories.media_repository_impl import get_media_repo


def get_media_repository() -> IMediaRepository:
    return get_media_repo()


MediaRepositoryDep = Annotated[IMediaRepository, Depends(get_media_repository)]
