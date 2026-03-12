from abc import ABC, abstractmethod
from uuid import UUID

from app.common.list import ListResult
from app.domain.entities.employee.intern import (
    InternGroupedByMentorResponse,
    InternIn,
    InternListFilters,
    InternOut,
    InternSnapshotFilters,
    InternStatsComparisonFilters,
    InternStatsComparisonOut,
    InternStatsFilters,
    InternStatsOut,
    InternUpdate,
)
from app.infrastructure.database import MentorProfile


class IInternRepository(ABC):
    @abstractmethod
    async def create(self, intern: InternIn) -> InternOut:
        raise NotImplementedError

    @abstractmethod
    async def list(self, filters: InternListFilters, employee: MentorProfile | None = None) -> ListResult[InternOut]:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, intern_id: UUID) -> InternOut | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, intern_id: UUID, intern_update: InternUpdate) -> InternOut | None:
        raise NotImplementedError

    @abstractmethod
    async def reassign_mentor(self, intern_id: UUID, new_mentor_id: UUID) -> InternOut | None:
        raise NotImplementedError

    @abstractmethod
    async def upload_avatar(self, intern_id: UUID, avatar_key: str) -> InternOut:
        raise NotImplementedError

    @abstractmethod
    async def remove_avatar(self, intern_id: UUID) -> InternOut:
        raise NotImplementedError

    @abstractmethod
    async def get_status_stats(
        self, filters: InternStatsFilters, employee: MentorProfile | None = None
    ) -> InternStatsOut:
        raise NotImplementedError

    @abstractmethod
    async def get_snapshot_stats(
        self, filters: InternSnapshotFilters, employee: MentorProfile | None = None
    ) -> InternStatsOut:
        raise NotImplementedError

    @abstractmethod
    async def get_stats_comparison(
        self, filters: InternStatsComparisonFilters, employee: MentorProfile | None = None
    ) -> InternStatsComparisonOut:
        raise NotImplementedError

    @abstractmethod
    async def list_grouped_by_mentor(
        self, filters: InternListFilters, employee: MentorProfile | None = None
    ) -> InternGroupedByMentorResponse:
        raise NotImplementedError
