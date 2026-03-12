from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repositories.intern_repository import IInternRepository
from app.domain.repositories.mentor_repository import IMentorRepository
from app.domain.repositories.request_repository import IRequestRepository
from app.domain.repositories.unit_repository import IUnitRepository
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.repositories.intern_repository_impl import InternRepository
from app.infrastructure.repositories.mentor_repository_impl import MentorRepository
from app.infrastructure.repositories.request_repository_impl import RequestRepository
from app.infrastructure.repositories.unit_repository_impl import UnitRepository


class UnitOfWork(IUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker | None = None,
        existing_session: AsyncSession | None = None,
        mentor_repo_factory: Callable[[AsyncSession], IMentorRepository] = MentorRepository,
        intern_repo_factory: Callable[[AsyncSession], IInternRepository] = InternRepository,
        request_repo_factory: Callable[[AsyncSession], IRequestRepository] = RequestRepository,
        unit_repo_factory: Callable[[AsyncSession], IUnitRepository] = UnitRepository,
    ):
        if existing_session is not None:
            self._session = existing_session
            self._owns_session = False
        elif session_factory is not None:
            self._session_factory = session_factory
            self._owns_session = True
        else:
            msg = "Either session_factory or existing_session must be provided"
            raise ValueError(msg)

        self._mentor_repo_factory = mentor_repo_factory
        self._mentor_repo: IMentorRepository | None = None
        self._intern_repo_factory = intern_repo_factory
        self._intern_repo: IInternRepository | None = None
        self._request_repo_factory = request_repo_factory
        self._request_repo: IRequestRepository | None = None
        self._unit_repo_factory = unit_repo_factory
        self._unit_repo: IUnitRepository | None = None
        self._committed = False

    async def __aenter__(self):
        if self._owns_session:
            self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session:
            if exc_type is not None or not self._committed:
                await self.rollback()
            await self._session.close()

    async def commit(self):
        await self._session.commit()
        self._committed = True

    async def rollback(self):
        await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def mentors(self) -> IMentorRepository:
        if self._mentor_repo is None:
            self._mentor_repo = self._mentor_repo_factory(self._session)
        return self._mentor_repo

    @property
    def interns(self) -> IInternRepository:
        if self._intern_repo is None:
            self._intern_repo = self._intern_repo_factory(self._session)
        return self._intern_repo

    @property
    def requests(self) -> IRequestRepository:
        if self._request_repo is None:
            self._request_repo = self._request_repo_factory(self._session)
        return self._request_repo

    @property
    def units(self) -> IUnitRepository:
        if self._unit_repo is None:
            self._unit_repo = self._unit_repo_factory(self._session)
        return self._unit_repo
