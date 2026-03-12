from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.entities.employee.intern import ReassignMentorRequest
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.unit_of_work import get_unit_of_work
from app.presentation.policies.base import EndpointPolicy


class CanReassignMentor(EndpointPolicy):
    permissions = {Permission.intern_reassign_mentor}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        intern_id: UUID,
        request: ReassignMentorRequest,
        uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        await self.check(employee, intern_id, uow)
        await self.validate_new_mentor_in_unit(employee, intern_id, request.new_mentor_id, uow)

        return employee

    @staticmethod
    async def check(employee: MentorProfile, intern_id: UUID, uow: IUnitOfWork) -> None:
        if employee.role == UserRole.superuser:
            return
        if employee.role == UserRole.head_mentor:
            intern = await uow.interns.get_one(intern_id)
            if intern is None:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")
            if intern.unit_id != employee.unit_id:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
            return
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    async def validate_new_mentor_in_unit(
        employee: MentorProfile, intern_id: UUID, new_mentor_id: UUID, uow: IUnitOfWork
    ) -> None:
        if employee.role != UserRole.head_mentor:
            return
        intern = await uow.interns.get_one(intern_id)
        if intern is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")
        mentor = await uow.mentors.get_one(new_mentor_id)
        if mentor is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")
        if mentor.unit_id != intern.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Head mentor can only reassign to a mentor in the same unit",
            )
