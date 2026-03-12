from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.list import ListResult
from app.domain.entities.employee.enum import InternshipStatus
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
    MentorWithInterns,
)
from app.domain.repositories.intern_repository import IInternRepository
from app.infrastructure.builders.intern_filters import InternQueryBuilder
from app.infrastructure.builders.intern_snapshot_builder import InternSnapshotQueryBuilder
from app.infrastructure.builders.intern_stats_builder import InternStatsQueryBuilder
from app.infrastructure.database.models.employee import InternProfile as InternProfileORM
from app.infrastructure.database.models.employee import MentorProfile


class InternRepository(IInternRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, intern: InternIn) -> InternOut:
        intern_orm = InternProfileORM(**intern.model_dump())
        self._session.add(intern_orm)

        await self._session.flush()
        await self._session.refresh(intern_orm)

        return InternOut.model_validate(intern_orm)

    async def list(self, filters: InternListFilters, employee: MentorProfile | None = None) -> ListResult[InternOut]:
        builder = InternQueryBuilder(filters, employee=employee)

        stmt = builder.build_items_with_total_query()
        result = await self._session.execute(stmt)

        rows = result.all()

        if not rows:
            return ListResult(items=[], total=0)

        items = [InternOut.model_validate(row[0]) for row in rows]
        total = rows[0][1]

        return ListResult(items=items, total=total)

    async def get_status_stats(
        self, filters: InternStatsFilters, employee: MentorProfile | None = None
    ) -> InternStatsOut:
        builder = InternStatsQueryBuilder(filters, employee=employee)
        result = await self._session.execute(builder.build())
        rows = result.all()

        counts: dict[InternshipStatus, int] = {row[0]: row[1] for row in rows}
        for status in builder.statuses:
            counts.setdefault(status, 0)

        # Get interns for each status using the builder
        interns_by_status: dict[InternshipStatus, list[InternOut]] = {}
        for status in builder.statuses:
            intern_stmt = builder.build_interns_query(status)
            intern_result = await self._session.execute(intern_stmt)
            intern_rows = intern_result.scalars().all()
            interns_by_status[status] = [InternOut.model_validate(intern) for intern in intern_rows]

        total = sum(counts.values())
        return InternStatsOut(total=total, by_status=counts, interns_by_status=interns_by_status)

    async def get_snapshot_stats(
        self, filters: InternSnapshotFilters, employee: MentorProfile | None = None
    ) -> InternStatsOut:
        builder = InternSnapshotQueryBuilder(filters, employee=employee)
        result = await self._session.execute(builder.build())
        rows = result.all()

        counts: dict[InternshipStatus, int] = {row[0]: row[1] for row in rows}
        statuses_to_process = set(filters.statuses) if filters.statuses else set()
        for row in rows:
            statuses_to_process.add(row[0])
        if not statuses_to_process:
            statuses_to_process = {s for s in InternshipStatus}
        for status in statuses_to_process:
            counts.setdefault(status, 0)

        interns_by_status: dict[InternshipStatus, list[InternOut]] = {}
        for status in statuses_to_process:
            intern_stmt = builder.build_interns_query(status)
            intern_result = await self._session.execute(intern_stmt)
            intern_rows = intern_result.scalars().all()
            interns_by_status[status] = [InternOut.model_validate(intern) for intern in intern_rows]

        total = sum(counts.values())
        return InternStatsOut(total=total, by_status=counts, interns_by_status=interns_by_status)

    async def get_stats_comparison(
        self, filters: InternStatsComparisonFilters, employee: MentorProfile | None = None
    ) -> InternStatsComparisonOut:
        current = await self.get_status_stats(
            InternStatsFilters(
                statuses=filters.statuses,
                period=filters.current_period,
                mentor_id=filters.mentor_id,
            ),
            employee=employee,
        )
        previous = await self.get_status_stats(
            InternStatsFilters(
                statuses=filters.statuses,
                period=filters.previous_period,
                mentor_id=filters.mentor_id,
            ),
            employee=employee,
        )
        absolute_change = current.total - previous.total
        percent_change = None
        if previous.total != 0:
            percent_change = (absolute_change / previous.total) * 100

        return InternStatsComparisonOut(
            current=current,
            previous=previous,
            absolute_change=absolute_change,
            percent_change=percent_change,
        )

    async def get_one(self, intern_id: UUID) -> InternOut | None:
        stmt = select(InternProfileORM).where(InternProfileORM.id == intern_id)
        result = await self._session.execute(stmt)
        intern_orm = result.scalar_one_or_none()

        if intern_orm is None:
            return None

        return InternOut.model_validate(intern_orm)

    async def update(self, intern_id: UUID, intern_update: InternUpdate) -> InternOut | None:
        stmt = select(InternProfileORM).where(InternProfileORM.id == intern_id)
        result = await self._session.execute(stmt)
        intern_orm = result.scalar_one_or_none()

        if intern_orm is None:
            return None

        update_dict = intern_update.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(intern_orm, key, value)
            if value is None and key == "military_occupation_at":
                setattr(intern_orm, key, value)

        if intern_orm.status == InternshipStatus.laid_off:
            intern_orm.hrm_id = None

        await self._session.flush()
        await self._session.refresh(intern_orm)

        return InternOut.model_validate(intern_orm)

    async def reassign_mentor(self, intern_id: UUID, new_mentor_id: UUID) -> InternOut | None:
        stmt = select(InternProfileORM).where(InternProfileORM.id == intern_id)
        result = await self._session.execute(stmt)
        intern_orm = result.scalar_one_or_none()

        if intern_orm is None:
            return None

        intern_orm.mentor_id = new_mentor_id

        await self._session.flush()
        await self._session.refresh(intern_orm)

        return InternOut.model_validate(intern_orm)

    async def upload_avatar(self, intern_id: UUID, avatar_key: str) -> InternOut:
        stmt = select(InternProfileORM).where(InternProfileORM.id == intern_id)
        result = await self._session.execute(stmt)
        intern_orm = result.scalar_one_or_none()

        if intern_orm is None:
            raise ValueError("Intern not found")

        intern_orm.avatar_key = avatar_key

        await self._session.flush()
        await self._session.refresh(intern_orm)

        return InternOut.model_validate(intern_orm)

    async def remove_avatar(self, intern_id: UUID) -> InternOut:
        stmt = select(InternProfileORM).where(InternProfileORM.id == intern_id)
        result = await self._session.execute(stmt)
        intern_orm = result.scalar_one_or_none()

        if intern_orm is None:
            raise ValueError("Intern not found")

        intern_orm.avatar_key = ""

        await self._session.flush()
        await self._session.refresh(intern_orm)

        return InternOut.model_validate(intern_orm)

    async def list_grouped_by_mentor(
        self, filters: InternListFilters, employee: MentorProfile | None = None
    ) -> InternGroupedByMentorResponse:
        builder = InternQueryBuilder(filters, employee=employee)
        stmt = builder.build_grouped_by_mentor_query()
        result = await self._session.execute(stmt)

        interns = [InternOut.model_validate(row) for row in result.scalars().all()]

        mentor_groups: dict[UUID, list[InternOut]] = {}
        for intern in interns:
            mentor_id = intern.mentor.id
            if mentor_id not in mentor_groups:
                mentor_groups[mentor_id] = []
            mentor_groups[mentor_id].append(intern)

        groups = []
        total_interns = 0
        for mentor_id, intern_list in mentor_groups.items():
            mentor_info = intern_list[0].mentor
            groups.append(
                MentorWithInterns(
                    mentor=mentor_info,
                    interns=intern_list,
                    total=len(intern_list),
                )
            )
            total_interns += len(intern_list)

        return InternGroupedByMentorResponse(
            groups=groups,
            total_mentors=len(groups),
            total_interns=total_interns,
        )
