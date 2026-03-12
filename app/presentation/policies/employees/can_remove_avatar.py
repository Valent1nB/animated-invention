from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.unit_of_work import get_unit_of_work
from app.presentation.policies.base import EndpointPolicy


class CanRemoveAvatar(EndpointPolicy):
    permissions = {Permission.mentor_update_self, Permission.intern_update, Permission.mentor_update}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
        employee_id: UUID,
    ) -> MentorProfile:
        await self.require_permission(employee)
        await self.check(employee, employee_id, uow)

        return employee

    @staticmethod
    async def check(employee: MentorProfile, employee_id: UUID, uow: IUnitOfWork) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor}:
            return

        if employee.id == employee_id:
            return

        intern = await uow.interns.get_one(employee_id)
        if intern is not None:
            if intern.mentor.id == employee.id:
                return

        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
