from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.entities.employee.mentor import ShortMentorIn
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.policies.base import EndpointPolicy


class CanCreateMentor(EndpointPolicy):
    permissions = {Permission.mentor_create}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        mentor_schema: ShortMentorIn,
    ) -> MentorProfile:
        await self.require_permission(employee)
        self.check(employee)
        self.validate_unit_id(employee, mentor_schema)

        return employee

    @staticmethod
    def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    def validate_unit_id(employee: MentorProfile, schema: ShortMentorIn) -> None:
        if employee.role != UserRole.head_mentor:
            return
        if schema.unit_id != employee.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Head mentor can only create mentors in their own unit",
            )
