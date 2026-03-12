from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.list import ListResult
from app.domain.entities.employee.enum import RequestStatus
from app.domain.entities.request.request import (
    RequestIn,
    RequestListFilters,
    RequestOut,
    RequestUpdate,
    RequestUpdateSelf,
)
from app.domain.repositories.request_repository import IRequestRepository
from app.infrastructure.builders.request_filters import RequestQueryBuilder
from app.infrastructure.database import MentorProfile
from app.infrastructure.database import Request as RequestORM


class RequestRepository(IRequestRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, request: RequestIn, requester_id: UUID) -> RequestOut:
        request_orm = RequestORM(
            requester_id=requester_id,
            receiver_id=request.receiver_id,
            topic=request.topic,
            intern_id=request.intern_id,
            extra_info=request.extra_info,
            status=RequestStatus.created,
        )
        self._session.add(request_orm)

        await self._session.flush()
        await self._session.refresh(request_orm)

        return RequestOut.model_validate(request_orm)

    async def list(self, filters: RequestListFilters, employee: MentorProfile | None = None) -> ListResult[RequestOut]:
        builder = RequestQueryBuilder(filters, employee=employee)

        stmt = builder.build_items_with_total_query()
        result = await self._session.execute(stmt)

        rows = result.all()

        if not rows:
            return ListResult(items=[], total=0)

        items = [RequestOut.model_validate(row[0]) for row in rows]
        total = rows[0][1]

        return ListResult(items=items, total=total)

    async def get_one(self, request_id: UUID) -> RequestOut | None:
        stmt = select(RequestORM).where(RequestORM.id == request_id)
        result = await self._session.execute(stmt)
        request_orm = result.scalar_one_or_none()

        if request_orm is None:
            return None

        return RequestOut.model_validate(request_orm)

    async def update(self, request_id: UUID, request_update: RequestUpdate) -> RequestOut | None:
        stmt = select(RequestORM).where(RequestORM.id == request_id)
        result = await self._session.execute(stmt)
        request_orm = result.scalar_one_or_none()

        if request_orm is None:
            return None

        update_dict = request_update.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(request_orm, key, value)

        if request_update.status in {RequestStatus.completed, RequestStatus.canceled}:
            if request_orm.closed_at is None:
                request_orm.closed_at = datetime.now()

        await self._session.flush()
        await self._session.refresh(request_orm)

        return RequestOut.model_validate(request_orm)

    async def update_self(
        self, request_id: UUID, requester_id: UUID, request_update: RequestUpdateSelf
    ) -> RequestOut | None:
        stmt = select(RequestORM).where(
            RequestORM.id == request_id,
            RequestORM.requester_id == requester_id,
            RequestORM.status == RequestStatus.created,
        )
        result = await self._session.execute(stmt)
        request_orm = result.scalar_one_or_none()

        if request_orm is None:
            return None

        update_dict = request_update.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(request_orm, key, value)

        await self._session.flush()
        await self._session.refresh(request_orm)

        return RequestOut.model_validate(request_orm)
