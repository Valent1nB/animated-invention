from abc import ABC, abstractmethod
from uuid import UUID

from app.common.list import ListResult
from app.domain.entities.employee.mentor import MentorIn, MentorListFilters, MentorOut, MentorUpdate, ShortMentorIn
from app.infrastructure.database import MentorProfile


class IMentorRepository(ABC):
    @abstractmethod
    async def create(self, mentor: MentorIn) -> MentorOut:
        raise NotImplementedError

    @abstractmethod
    async def list(self, filters: MentorListFilters, employee: MentorProfile | None = None) -> ListResult[MentorOut]:
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, mentor_id: UUID) -> MentorOut | None:
        raise NotImplementedError

    @abstractmethod
    async def attach_to_user(self, user_id: UUID, mentor_id: UUID) -> MentorOut:
        raise NotImplementedError

    @abstractmethod
    async def get_one_by_email(self, email: str) -> MentorOut | None:
        raise NotImplementedError

    @abstractmethod
    async def get_head_mentors(self, unit_id: UUID | None = None) -> ListResult[MentorOut]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, mentor_id: UUID, mentor_update: MentorUpdate) -> MentorOut | None:
        raise NotImplementedError

    @abstractmethod
    async def archive(self, mentor_id: UUID) -> MentorOut | None:
        raise NotImplementedError

    @abstractmethod
    async def recover(self, mentor_id: UUID) -> MentorOut | None:
        raise NotImplementedError

    @abstractmethod
    async def upload_avatar(self, mentor_id: UUID, avatar_key: str) -> MentorOut:
        raise NotImplementedError

    @abstractmethod
    async def remove_avatar(self, mentor_id: UUID) -> MentorOut:
        raise NotImplementedError

    async def create_without_user(self, mentor_schema: ShortMentorIn) -> MentorOut:
        raise NotImplementedError
