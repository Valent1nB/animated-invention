from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.unit_of_work import get_unit_of_work
from app.presentation.policies.base import EndpointPolicy


class CanGetMentor(EndpointPolicy):
    permissions = {Permission.mentor_get_self, Permission.mentor_get}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        mentor_id: UUID,
        uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        await self.check(employee, mentor_id, uow)

        return employee

    @staticmethod
    async def check(employee: MentorProfile, mentor_id: UUID, uow: IUnitOfWork) -> None:
        if employee.role == UserRole.superuser:
            return
        if employee.role == UserRole.mentor and employee.id == mentor_id:
            return
        if employee.role == UserRole.head_mentor:
            mentor = await uow.mentors.get_one(mentor_id)
            if mentor is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")
            if mentor.unit_id != employee.unit_id:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
            return
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
