from abc import ABC, abstractmethod

from app.domain.repositories.intern_repository import IInternRepository
from app.domain.repositories.mentor_repository import IMentorRepository
from app.domain.repositories.request_repository import IRequestRepository
from app.domain.repositories.unit_repository import IUnitRepository


class IUnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @property
    @abstractmethod
    def mentors(self) -> IMentorRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def interns(self) -> IInternRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def requests(self) -> IRequestRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def units(self) -> IUnitRepository:
        raise NotImplementedError
