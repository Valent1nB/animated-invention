from __future__ import annotations

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.sql import Select

from app.common.pagination import Pagination
from app.domain.entities.employee.enum import RequestSort, UserRole
from app.domain.entities.request.request import RequestListFilters
from app.infrastructure.builders.base import IListQueryBuilder
from app.infrastructure.database import MentorProfile, Request
from app.infrastructure.database.models.employee import MentorProfile as MentorProfileORM


class RequestQueryBuilder(IListQueryBuilder[RequestListFilters]):
    def base_stmt(self) -> Select:
        return select(Request)

    def pagination(self) -> Pagination:
        return self.filters.pagination

    def apply_filters(self, stmt: Select) -> Select:
        f = self.filters
        r = Request

        if f.status is not None:
            stmt = stmt.where(r.status == f.status)

        if f.topic is not None:
            stmt = stmt.where(r.topic == f.topic)

        if f.requester_id is not None:
            stmt = stmt.where(r.requester_id == f.requester_id)

        if f.receiver_id is not None:
            stmt = stmt.where(r.receiver_id == f.receiver_id)

        if f.unit_id is not None:
            req_alias = MentorProfileORM.__table__.alias("req_unit_filter")
            rec_alias = MentorProfileORM.__table__.alias("rec_unit_filter")
            stmt = stmt.join(req_alias, r.requester_id == req_alias.c.id)
            stmt = stmt.join(rec_alias, r.receiver_id == rec_alias.c.id)
            stmt = stmt.where(or_(req_alias.c.unit_id == f.unit_id, rec_alias.c.unit_id == f.unit_id))

        return stmt

    def apply_search(self, stmt: Select) -> Select:
        # Requests don't have search functionality yet
        return stmt

    def apply_order(self, stmt: Select) -> Select:
        order = self.filters.order
        direction_fn = desc if order.direction == "desc" else asc
        r = Request

        sort_map = {
            RequestSort.created_at: r.created_at,
            RequestSort.status: r.status,
            RequestSort.topic: r.topic,
        }

        sort_expr = sort_map[order.by]

        return stmt.order_by(
            direction_fn(sort_expr).nulls_last(),
            desc(r.id),
        )

    def apply_constraints(self, stmt: Select, employee: MentorProfile) -> Select:
        """
        Apply role-based constraints to request queries.

        - superuser: no constraints (may filter by unit_id in filters)
        - head_mentor: only show requests where requester or receiver is in their unit
        - mentor: only show requests where requester_id == employee.id
        """
        if employee.role == UserRole.superuser:
            return stmt

        if employee.role == UserRole.head_mentor:
            requester = MentorProfileORM.__table__.alias("req")
            receiver = MentorProfileORM.__table__.alias("rec")
            stmt = stmt.join(requester, Request.requester_id == requester.c.id)
            stmt = stmt.join(receiver, Request.receiver_id == receiver.c.id)
            stmt = stmt.where(
                or_(
                    requester.c.unit_id == employee.unit_id,
                    receiver.c.unit_id == employee.unit_id,
                )
            )
        elif employee.role == UserRole.mentor:
            stmt = stmt.where(Request.requester_id == employee.id)

        return stmt
