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


class CanEditIntern(EndpointPolicy):
    permissions = {Permission.intern_update}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
        intern_id: UUID,
    ) -> MentorProfile:
        await self.require_permission(employee)
        await self.check(employee, intern_id, uow)

        return employee

    @staticmethod
    async def check(employee: MentorProfile, intern_id: UUID, uow: IUnitOfWork) -> None:
        if employee.role == UserRole.superuser:
            return

        intern = await uow.interns.get_one(intern_id)
        if intern is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")

        if employee.role == UserRole.head_mentor:
            if intern.unit_id != employee.unit_id:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
            return

        if intern.mentor.id != employee.id:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
