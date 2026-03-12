from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.sql import Select

from app.common.pagination import (
    Pagination,
    add_total_over,
    apply_pagination,
    total_stmt,
)
from app.domain.entities.employee.enum import UserRole
from app.infrastructure.database import MentorProfile


class IListQueryBuilder[FiltersT](ABC):
    """
    Base class for building list queries with filtering, searching,
    ordering and pagination.

    This builder is intentionally state-less:
    each build_* method starts from a base SELECT statement
    and returns a new SQLAlchemy Select object.
    """

    def __init__(self, filters: FiltersT, employee: MentorProfile | None = None):
        """
        :param filters: A filter specification object
                        (usually a Pydantic model).
        :param employee: Optional employee profile to apply role-based constraints.
        """
        self.filters = filters
        self.employee = employee

    @abstractmethod
    def base_stmt(self) -> Select:
        """
        Return the base SELECT statement for the query.

        Example:
            return select(MentorProfile)

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def apply_filters(self, stmt: Select) -> Select:
        """
        Apply field-based filters to the statement.

        Override this method to add WHERE conditions
        based on filter values.

        Default implementation does nothing.
        """
        return stmt

    def apply_search(self, stmt: Select) -> Select:
        """
        Apply full-text or multi-field search conditions.

        Override this method to add search logic.

        Default implementation does nothing.
        """
        return stmt

    def apply_order(self, stmt: Select) -> Select:
        """
        Apply ORDER BY clauses to the statement.

        Override this method to add sorting logic.

        Default implementation does nothing.
        """
        return stmt

    def _apply_common(self, stmt: Select) -> Select:
        """
        Apply filters, search, ordering and constraints in a fixed order.

        This is a template method and should not be overridden.
        """
        stmt = self.apply_filters(stmt)
        stmt = self.apply_search(stmt)
        stmt = self.apply_order(stmt)
        if self.employee is not None:
            stmt = self.apply_constraints(stmt, self.employee)
        return stmt

    @abstractmethod
    def pagination(self) -> Pagination:
        """
        Return pagination parameters (limit / offset).

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def build_items_query(self, stmt: Select | None = None) -> Select:
        """
        Build a SELECT query that returns paginated items.

        :param stmt: Optional base statement to start from.
        :return: SQLAlchemy Select with filters, search, order and pagination.
        """
        stmt = self._apply_common(stmt or self.base_stmt())
        return apply_pagination(stmt, self.pagination())

    def build_total_query(self, stmt: Select | None = None) -> Select:
        """
        Build a SELECT query that returns the total number of items
        matching filters and search (without pagination).

        :param stmt: Optional base statement to start from.
        :return: SELECT count(*) FROM (<filtered query>)
        """
        stmt = self.apply_filters(stmt or self.base_stmt())
        stmt = self.apply_search(stmt)
        if self.employee is not None:
            stmt = self.apply_constraints(stmt, self.employee)
        return total_stmt(stmt)

    def build_items_with_total_query(self, stmt: Select | None = None) -> Select:
        """
        Build a single SELECT query that returns paginated items
        together with the total count using a window function
        (count(*) OVER ()).

        :param stmt: Optional base statement to start from.
        :return: SQLAlchemy Select with items and total count.
        """
        stmt = self._apply_common(stmt or self.base_stmt())
        stmt = add_total_over(stmt, label="total")
        return apply_pagination(stmt, self.pagination())

    def apply_constraints(self, stmt: Select, employee: MentorProfile) -> Select:
        """
        Apply role-based constraints to the query based on the employee's role.

        - head_mentor and superuser: no constraints applied
        - mentor: constraints are applied (to be overridden in subclasses)

        :param employee: MentorProfile of the requesting user
        :param stmt: Base statement to apply constraints to
        :return: SQLAlchemy Select with constraints applied
        """
        # head_mentor and superuser have no constraints
        if employee.role in {UserRole.head_mentor, UserRole.superuser}:
            return stmt

        # For mentor role, subclasses should override this method
        # to apply specific constraints
        return stmt
