from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import UserRole
from app.domain.entities.employee.intern import InternListFilters
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.intern import get_intern_list_filters
from app.presentation.policies.base import EndpointPolicy


class CanGetInternsGroupedByMentor(EndpointPolicy):
    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        filters: Annotated[InternListFilters, Depends(get_intern_list_filters)],
    ) -> MentorProfile:
        await self.check(employee)
        self.validate_unit_id(employee, filters)
        return employee

    @staticmethod
    async def check(employee: MentorProfile) -> None:
        if employee.role not in {UserRole.superuser, UserRole.head_mentor}:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Only head mentors and superusers can view grouped interns",
            )

    @staticmethod
    def validate_unit_id(employee: MentorProfile, filters: InternListFilters) -> None:
        if employee.role != UserRole.head_mentor:
            return
        if filters.unit_id is not None and filters.unit_id != employee.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Head mentor can only filter by their own unit",
            )
        filters.unit_id = employee.unit_id
