from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.entities.employee.intern import InternSnapshotFilters, InternStatsComparisonFilters, InternStatsFilters
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.intern import (
    get_historical_intern_stats_filters,
    get_intern_snapshot_filters,
    get_intern_stats_comparison_filters,
)
from app.presentation.policies.base import EndpointPolicy


def validate_unit_id(
    employee: MentorProfile, filters: InternStatsFilters | InternStatsComparisonFilters | InternSnapshotFilters
) -> None:
    if employee.role != UserRole.head_mentor:
        return
    if filters.unit_id is not None and filters.unit_id != employee.unit_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Head mentor can only filter by their own unit",
        )
    filters.unit_id = employee.unit_id


class CanGetInternStats(EndpointPolicy):
    permissions = {Permission.intern_get_stats}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        filters: Annotated[InternStatsFilters, Depends(get_historical_intern_stats_filters)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        self.check(employee)
        validate_unit_id(employee, filters)
        self.validate_mentor_id(employee, filters)
        return employee

    @staticmethod
    def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

    @staticmethod
    def validate_mentor_id(employee: MentorProfile, filters: InternStatsFilters) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

        if filters.mentor_id is not None and filters.mentor_id != employee.id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only view statistics for your own interns",
            )


class CanCompareInternStats(EndpointPolicy):
    permissions = {Permission.intern_get_stats}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        filters: Annotated[InternStatsComparisonFilters, Depends(get_intern_stats_comparison_filters)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        self.check(employee)
        validate_unit_id(employee, filters)
        self.validate_mentor_id(employee, filters)
        return employee

    @staticmethod
    def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

    @staticmethod
    def validate_mentor_id(employee: MentorProfile, filters: InternStatsComparisonFilters) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

        if filters.mentor_id is not None and filters.mentor_id != employee.id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only view statistics for your own interns",
            )


class CanGetInternSnapshotStats(EndpointPolicy):
    permissions = {Permission.intern_get_stats}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        filters: Annotated[InternSnapshotFilters, Depends(get_intern_snapshot_filters)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        self.check(employee)
        validate_unit_id(employee, filters)
        self.validate_mentor_id(employee, filters)
        return employee

    @staticmethod
    def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

    @staticmethod
    def validate_mentor_id(employee: MentorProfile, filters: InternSnapshotFilters) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

        if filters.mentor_id is not None and filters.mentor_id != employee.id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only view statistics for your own interns",
            )
