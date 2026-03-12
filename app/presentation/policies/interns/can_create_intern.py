from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.entities.employee.intern import InternIn
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.unit_of_work import get_unit_of_work
from app.presentation.policies.base import EndpointPolicy


class CanCreateIntern(EndpointPolicy):
    permissions = {Permission.intern_create}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        intern_schema: InternIn,
        uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        self.check(employee)
        self.validate_unit_id(employee, intern_schema)
        await self.validate_mentor_in_unit(intern_schema, uow)

        return employee

    @staticmethod
    def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    def validate_unit_id(employee: MentorProfile, schema: InternIn) -> None:
        if employee.role != UserRole.head_mentor:
            return
        if schema.unit_id != employee.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Head mentor can only create interns in their own unit",
            )

    @staticmethod
    async def validate_mentor_in_unit(schema: InternIn, uow: IUnitOfWork) -> None:
        mentor = await uow.mentors.get_one(schema.mentor_id)
        if mentor is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")
        if mentor.unit_id != schema.unit_id:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Mentor must be in the same unit as the intern",
            )
