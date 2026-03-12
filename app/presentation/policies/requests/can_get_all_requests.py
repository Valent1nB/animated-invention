from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.entities.request import RequestListFilters
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.request import get_request_list_filters
from app.presentation.policies.base import EndpointPolicy


class CanGetAllRequests(EndpointPolicy):
    permissions = {Permission.request_get_all}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        filters: Annotated[RequestListFilters, Depends(get_request_list_filters)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        await self.check(employee)
        self.validate_unit_id(employee, filters)
        self.validate_requester_id(employee, filters)

        return employee

    @staticmethod
    async def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

    @staticmethod
    def validate_unit_id(employee: MentorProfile, filters: RequestListFilters) -> None:
        if employee.role != UserRole.head_mentor:
            return
        if filters.unit_id is not None and filters.unit_id != employee.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Head mentor can only filter by their own unit",
            )
        filters.unit_id = employee.unit_id

    @staticmethod
    def validate_requester_id(employee: MentorProfile, filters: RequestListFilters) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

        if filters.requester_id is not None and filters.requester_id != employee.id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You can only view your own requests",
            )
