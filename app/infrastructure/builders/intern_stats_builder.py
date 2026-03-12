from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.sql import Select

from app.common.pagination import Pagination, apply_pagination
from app.domain.entities.employee.enum import InternshipStatus, UserRole
from app.domain.entities.employee.intern import InternListFilters, InternStatsFilters
from app.infrastructure.builders.base_stats import BaseStatsQueryBuilder
from app.infrastructure.builders.intern_filters import InternQueryBuilder
from app.infrastructure.database import InternProfile, MentorProfile


class InternStatsQueryBuilder(BaseStatsQueryBuilder):
    """
    Builder for intern status statistics queries.
    """

    def __init__(self, filters: InternStatsFilters, employee: MentorProfile | None = None):
        self.filters = filters
        self.employee = employee
        self._statuses = (
            list(filters.statuses) if filters.statuses else [InternshipStatus.laid_off, InternshipStatus.sold]
        )
        self._start_dt, self._end_dt = self._date_bounds(filters.period.start_date, filters.period.end_date)

    @property
    def statuses(self) -> list[InternshipStatus]:
        return self._statuses

    def base_stmt(self) -> Select:
        return select(InternProfile.status, func.count(InternProfile.id))

    def _apply_date_filters(self, stmt: Select) -> Select:
        return stmt.where(
            InternProfile.end_date >= self._start_dt,
            InternProfile.end_date < self._end_dt,
        )

    def _apply_mentor_filter(self, stmt: Select) -> Select:
        mentor_id = self.filters.mentor_id
        if self.employee is not None and self.employee.role not in {UserRole.superuser, UserRole.head_mentor}:
            mentor_id = self.employee.id

        if mentor_id is not None:
            stmt = stmt.where(InternProfile.mentor_id == mentor_id)

        return stmt

    def _apply_unit_filter(self, stmt: Select) -> Select:
        unit_id = self.filters.unit_id
        if self.employee is not None and self.employee.role in [UserRole.head_mentor, UserRole.mentor]:
            unit_id = self.employee.unit_id
        if unit_id is not None:
            stmt = stmt.where(InternProfile.unit_id == unit_id)
        return stmt

    def apply_filters(self, stmt: Select) -> Select:
        stmt = stmt.where(InternProfile.status.in_(self._statuses))
        stmt = self._apply_date_filters(stmt)
        stmt = self._apply_mentor_filter(stmt)
        stmt = self._apply_unit_filter(stmt)
        return stmt

    def build(self) -> Select:
        stmt = self.base_stmt()
        stmt = self.apply_filters(stmt)
        return stmt.group_by(InternProfile.status)

    def build_interns_query(self, status: InternshipStatus) -> Select:
        intern_list_filters = InternListFilters(
            status=[status],
            mentor_id=None,  # Will be applied by _apply_mentor_filter
            pagination=Pagination(limit=200, offset=0),
        )
        intern_builder = InternQueryBuilder(intern_list_filters, employee=self.employee)
        intern_stmt = intern_builder.base_stmt()
        intern_stmt = intern_builder.apply_filters(intern_stmt)
        intern_stmt = intern_builder.apply_search(intern_stmt)
        if self.employee is not None:
            intern_stmt = intern_builder.apply_constraints(intern_stmt, self.employee)
        intern_stmt = intern_builder.apply_order(intern_stmt)

        intern_stmt = self._apply_date_filters(intern_stmt)
        intern_stmt = self._apply_mentor_filter(intern_stmt)
        intern_stmt = self._apply_unit_filter(intern_stmt)
        intern_stmt = apply_pagination(intern_stmt, intern_builder.pagination())
        return intern_stmt
