from typing import Annotated

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.domain.entities.employee.enum import Permission, UserRole
from app.domain.entities.request.request import RequestIn
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.unit_of_work import get_unit_of_work
from app.presentation.policies.base import EndpointPolicy


class CanCreateRequest(EndpointPolicy):
    permissions = {Permission.request_create}

    async def __call__(
        self,
        employee: Annotated[MentorProfile, Depends(get_current_employee)],
        request_schema: RequestIn,
        uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    ) -> MentorProfile:
        await self.require_permission(employee)
        self.check(employee)
        await self.validate_receiver_in_unit(employee, request_schema, uow)
        await self.validate_intern_in_unit(employee, request_schema, uow)

        return employee

    @staticmethod
    def check(employee: MentorProfile) -> None:
        if employee.role in {UserRole.superuser, UserRole.head_mentor, UserRole.mentor}:
            return
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    async def validate_receiver_in_unit(employee: MentorProfile, schema: RequestIn, uow: IUnitOfWork) -> None:
        if employee.role == UserRole.superuser:
            return
        receiver = await uow.mentors.get_one(schema.receiver_id)
        if receiver is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Receiver not found")
        if receiver.unit_id != employee.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Mentor can only create requests to head mentors in their own unit",
            )
        if employee.role == UserRole.mentor and receiver.role == UserRole.mentor:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Mentor can only create requests to head mentors"
            )

    @staticmethod
    async def validate_intern_in_unit(employee: MentorProfile, schema: RequestIn, uow: IUnitOfWork) -> None:
        if employee.role == UserRole.superuser:
            return

        if not schema.intern_id:
            return

        intern = await uow.interns.get_one(schema.intern_id)

        if intern is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")

        if intern.unit_id != employee.unit_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Mentor can only create requests to interns in their own unit",
            )

        if employee.role == UserRole.mentor and intern.mentor.id != employee.id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Mentor can only create requests to their own interns",
            )
