from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.application.services.permission_service import PermissionService
from app.application.use_cases.employees.remove_avatar_use_case import RemoveAvatarUseCase
from app.application.use_cases.employees.upload_avatar_use_case import UploadAvatarUseCase
from app.domain.entities.employee.enum import Permission
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile, User
from app.presentation.auth_backend import current_active_user
from app.presentation.dependencies.db import get_async_session
from app.presentation.dependencies.media import MediaRepositoryDep
from app.presentation.dependencies.unit_of_work import get_unit_of_work


async def get_current_employee(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(current_active_user)],
) -> MentorProfile:
    if not user.mentor_profile:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Employee not found")

    await db_session.refresh(user.mentor_profile)

    return user.mentor_profile


def get_upload_avatar_use_case(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    media_repo: MediaRepositoryDep,
) -> UploadAvatarUseCase:
    return UploadAvatarUseCase(uow, media_repo)


def get_remove_avatar_use_case(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
    media_repo: MediaRepositoryDep,
) -> RemoveAvatarUseCase:
    return RemoveAvatarUseCase(uow, media_repo)


class HasPermission:
    def __init__(self, permission: Permission):
        self.permission = permission

    async def __call__(self, employee: Annotated[MentorProfile, Depends(get_current_employee)]):
        permissions = PermissionService.get_permissions(employee.role)

        if self.permission in permissions:
            return employee

        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
