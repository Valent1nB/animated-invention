from typing import Annotated

from fastapi import Depends

from app.domain.entities.employee.enum import Permission
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.policies.base import EndpointPolicy


class CanGetUnits(EndpointPolicy):
    """Only superuser can list all units (for filter dropdown)."""

    permissions = {Permission.unit_get_all}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        return employee
