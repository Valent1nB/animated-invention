from abc import ABC, abstractmethod
from uuid import UUID

from app.common.list import ListResult
from app.domain.entities.request.request import (
    RequestIn,
    RequestListFilters,
    RequestOut,
    RequestUpdate,
    RequestUpdateSelf,
)
from app.infrastructure.database import MentorProfile


class IRequestRepository(ABC):
    @abstractmethod
    async def create(self, request: RequestIn, requester_id: UUID) -> RequestOut:
        raise NotImplementedError

    @abstractmethod
    async def list(self, filters: RequestListFilters, employee: MentorProfile | None = None) -> ListResult[RequestOut]:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, request_id: UUID) -> RequestOut | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, request_id: UUID, request_update: RequestUpdate) -> RequestOut | None:
        raise NotImplementedError

    @abstractmethod
    async def update_self(
        self, request_id: UUID, requester_id: UUID, request_update: RequestUpdateSelf
    ) -> RequestOut | None:
        raise NotImplementedError
