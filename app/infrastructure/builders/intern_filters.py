from __future__ import annotations

from sqlalchemy import asc, desc, func, literal, or_, select
from sqlalchemy.sql import Select

from app.common.pagination import Pagination
from app.domain.entities.employee.enum import InternSort, UserRole
from app.domain.entities.employee.intern import InternListFilters
from app.infrastructure.builders.base import IListQueryBuilder
from app.infrastructure.database import InternProfile, MentorProfile


class InternQueryBuilder(IListQueryBuilder[InternListFilters]):
    def base_stmt(self) -> Select:
        return select(InternProfile)

    def pagination(self) -> Pagination:
        return self.filters.pagination

    def full_name_expr(self):
        i = InternProfile
        return func.concat(i.first_name, literal(" "), i.last_name)

    def apply_filters(self, stmt: Select) -> Select:
        f = self.filters
        i = InternProfile

        if f.status is not None:
            stmt = stmt.where(i.status.in_(f.status))

        if f.mentor_id is not None:
            stmt = stmt.where(i.mentor_id == f.mentor_id)

        if f.employment_status is not None:
            stmt = stmt.where(i.employment_status.in_(f.employment_status))

        if f.english_level is not None:
            stmt = stmt.where(i.english_level.in_(f.english_level))

        if f.ready_for_sale is not None:
            stmt = stmt.where(i.ready_for_sale == f.ready_for_sale)

        if f.unit_id is not None:
            stmt = stmt.where(i.unit_id == f.unit_id)

        if f.military_status is not None:
            stmt = stmt.where(i.military_status.in_(f.military_status))

        return stmt

    def apply_search(self, stmt: Select) -> Select:
        if not self.filters.search:
            return stmt

        q = f"%{self.filters.search}%"
        i = InternProfile

        return stmt.where(
            or_(
                i.email.ilike(q),
                i.city.ilike(q),
                i.first_name.ilike(q),
                i.last_name.ilike(q),
                self.full_name_expr().ilike(q),
            )
        )

    def apply_order(self, stmt: Select) -> Select:
        order = self.filters.order
        direction_fn = desc if order.direction == "desc" else asc
        i = InternProfile

        sort_map = {
            InternSort.full_name: self.full_name_expr(),
            InternSort.status: i.status,
            InternSort.start_date: i.start_date,
            InternSort.end_date: i.end_date,
            InternSort.internship_length: i.internship_length,
            InternSort.city: i.city,
            InternSort.email: i.email,
            InternSort.employment_status: i.employment_status,
            InternSort.english_level: i.english_level,
            InternSort.university_name: i.university_name,
            InternSort.ready_for_sale: i.ready_for_sale,
            InternSort.military_status: i.military_status,
        }

        sort_expr = sort_map[order.by]

        return stmt.order_by(
            direction_fn(sort_expr).nulls_last(),
            asc(i.id),
        )

    def apply_constraints(self, stmt: Select, employee: MentorProfile) -> Select:
        """
        Apply role-based constraints to intern queries.

        - superuser: no constraints (may filter by unit_id in filters)
        - head_mentor: only show interns in their unit
        - mentor: only show interns assigned to this mentor (mentor_id == employee.id)
        """
        if employee.role == UserRole.superuser:
            return stmt

        if employee.role == UserRole.head_mentor:
            stmt = stmt.where(InternProfile.unit_id == employee.unit_id)
        elif employee.role == UserRole.mentor:
            stmt = stmt.where(InternProfile.mentor_id == employee.id).where(InternProfile.unit_id == employee.unit_id)

        return stmt

    def build_grouped_by_mentor_query(self) -> Select:
        """
        Build a query for grouping interns by mentor.
        Returns all interns sorted by mentor name and then by intern name.
        """
        i = InternProfile
        m = MentorProfile

        stmt = select(i).join(m, i.mentor_id == m.id)

        stmt = self.apply_filters(stmt)
        stmt = self.apply_search(stmt)

        if self.employee is not None:
            stmt = self.apply_constraints(stmt, self.employee)

        stmt = stmt.order_by(
            asc(self.full_name_expr()),
        )

        return stmt
