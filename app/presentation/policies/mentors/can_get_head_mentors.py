from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import Permission, UserRole
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.policies.base import EndpointPolicy


class CanGetHeadMentors(EndpointPolicy):
    permissions = {Permission.mentor_get_head}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        await self.check(employee)

        return employee

    @staticmethod
    async def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor, UserRole.mentor}:
            return
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
