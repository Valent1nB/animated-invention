from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.sql import Select

from app.common.pagination import Pagination, apply_pagination
from app.domain.entities.employee.enum import InternshipStatus, UserRole
from app.domain.entities.employee.intern import InternListFilters, InternSnapshotFilters
from app.infrastructure.builders.intern_filters import InternQueryBuilder
from app.infrastructure.database import InternProfile, MentorProfile


class InternSnapshotQueryBuilder:
    """
    Builder for current snapshot statistics (no date range).
    """

    def __init__(self, filters: InternSnapshotFilters, employee: MentorProfile | None = None):
        self.filters = filters
        self.employee = employee

    def base_stmt(self) -> Select:
        return select(InternProfile.status, func.count(InternProfile.id))

    def _apply_snapshot_filters(self, stmt: Select) -> Select:
        """Apply snapshot-specific filters (english_levels, cities, ready_for_sale)."""
        f = self.filters

        if f.english_levels:
            stmt = stmt.where(InternProfile.english_level.in_(list(f.english_levels)))

        if f.cities:
            stmt = stmt.where(InternProfile.city.in_(list(f.cities)))

        if f.ready_for_sale is not None:
            stmt = stmt.where(InternProfile.ready_for_sale == f.ready_for_sale)

        return stmt

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
        f = self.filters

        if f.statuses:
            stmt = stmt.where(InternProfile.status.in_(list(f.statuses)))

        stmt = self._apply_snapshot_filters(stmt)
        stmt = self._apply_mentor_filter(stmt)
        stmt = self._apply_unit_filter(stmt)

        return stmt

    def build(self) -> Select:
        stmt = self.base_stmt()
        stmt = self.apply_filters(stmt)
        return stmt.group_by(InternProfile.status)

    def build_interns_query(self, status: InternshipStatus) -> Select:
        """
        Build a query to get interns for a specific status with the same filters as snapshot stats.
        """
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

        intern_stmt = self._apply_snapshot_filters(intern_stmt)
        intern_stmt = self._apply_mentor_filter(intern_stmt)
        intern_stmt = self._apply_unit_filter(intern_stmt)
        intern_stmt = apply_pagination(intern_stmt, intern_builder.pagination())
        return intern_stmt
