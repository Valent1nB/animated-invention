from __future__ import annotations

from sqlalchemy import asc, desc, func, literal, or_, select
from sqlalchemy.sql import Select

from app.common.pagination import Pagination
from app.domain.entities.employee.enum import MentorSort, UserRole
from app.domain.entities.employee.mentor import MentorListFilters
from app.infrastructure.builders.base import IListQueryBuilder
from app.infrastructure.database import MentorProfile


class MentorQueryBuilder(IListQueryBuilder[MentorListFilters]):
    def base_stmt(self) -> Select:
        return select(MentorProfile)

    def pagination(self) -> Pagination:
        return self.filters.pagination

    def full_name_expr(self):
        m = MentorProfile
        return func.concat(m.first_name, literal(" "), m.last_name)

    def apply_filters(self, stmt: Select) -> Select:
        f = self.filters
        m = MentorProfile

        if f.available is not None:
            stmt = stmt.where(m.available.is_(f.available))

        if f.available_for_interview is not None:
            stmt = stmt.where(m.available_for_interview.is_(f.available_for_interview))

        if f.role is not None:
            stmt = stmt.where(m.role.in_(f.role))

        if f.unit_id is not None:
            stmt = stmt.where(m.unit_id == f.unit_id)

        return stmt

    def apply_constraints(self, stmt: Select, employee: MentorProfile) -> Select:
        if employee.role == UserRole.superuser:
            return stmt
        if employee.role == UserRole.head_mentor:
            stmt = stmt.where(MentorProfile.unit_id == employee.unit_id)
        elif employee.role == UserRole.mentor:
            stmt = stmt.where(MentorProfile.id == employee.id).where(MentorProfile.unit_id == employee.unit_id)
        return stmt

    def apply_search(self, stmt: Select) -> Select:
        if not self.filters.search:
            return stmt

        q = f"%{self.filters.search}%"
        m = MentorProfile

        return stmt.where(
            or_(
                m.email.ilike(q),
                m.city.ilike(q),
                m.first_name.ilike(q),
                m.last_name.ilike(q),
                self.full_name_expr().ilike(q),
            )
        )

    def apply_order(self, stmt: Select) -> Select:
        order = self.filters.order
        direction_fn = desc if order.direction == "desc" else asc
        m = MentorProfile

        sort_map = {
            MentorSort.full_name: self.full_name_expr(),
            MentorSort.interns_active: m.interns_active,
            MentorSort.available: m.available,
            MentorSort.available_for_interview: m.available_for_interview,
            MentorSort.role: m.role,
            MentorSort.city: m.city,
            MentorSort.email: m.email,
        }

        sort_expr = sort_map[order.by]

        return stmt.order_by(
            direction_fn(sort_expr).nulls_last(),
            asc(m.id),
        )
