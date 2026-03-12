from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.application.use_cases.employees.remove_avatar_use_case import RemoveAvatarUseCase
from app.application.use_cases.employees.upload_avatar_use_case import UploadAvatarUseCase
from app.domain.entities.employee.intern import InternOut
from app.domain.entities.employee.mentor import MentorOut
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import (
    get_remove_avatar_use_case,
    get_upload_avatar_use_case,
)
from app.presentation.policies.employees.can_remove_avatar import CanRemoveAvatar
from app.presentation.policies.employees.can_upload_avatar import CanUploadAvatar

router = APIRouter(prefix="/employee", tags=["employee"])


FullInfoEmployeeOutSchema = Union[MentorOut, InternOut]


@router.post("/{employee_id}/upload-avatar", status_code=HTTP_201_CREATED)
async def upload_avatar(
    employee_id: UUID,
    _: Annotated[MentorProfile, Depends(CanUploadAvatar())],
    use_case: UploadAvatarUseCase = Depends(get_upload_avatar_use_case),
    image: UploadFile = File(..., description="Avatar file"),
) -> FullInfoEmployeeOutSchema:
    key = f"avatars/{employee_id}/{image.filename}"
    return await use_case(employee_id, key, image.file, commit=True)


@router.delete("/{employee_id}/remove-avatar", status_code=HTTP_204_NO_CONTENT)
async def remove_avatar(
    employee_id: UUID,
    _: Annotated[MentorProfile, Depends(CanRemoveAvatar())],
    use_case: RemoveAvatarUseCase = Depends(get_remove_avatar_use_case),
):
    await use_case(employee_id, commit=True)
