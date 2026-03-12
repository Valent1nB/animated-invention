from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.application.use_cases.mentors.archive_mentor_use_case import ArchiveMentorUseCase
from app.application.use_cases.mentors.create_mentor_use_case import CreateMentorUseCase
from app.application.use_cases.mentors.get_all_mentors_use_case import GetAllMentorsUseCase
from app.application.use_cases.mentors.get_head_mentors_use_case import GetHeadMentorsUseCase
from app.application.use_cases.mentors.get_mentor_use_case import GetMentorUseCase
from app.application.use_cases.mentors.recover_mentor_use_case import RecoverMentorUseCase
from app.application.use_cases.mentors.update_mentor_use_case import UpdateMentorUseCase
from app.common.list import ListResult
from app.domain.entities.employee.enum import Role
from app.domain.entities.employee.mentor import (
    FullMentorOut,
    MentorListFilters,
    MentorListResponse,
    MentorOut,
    MentorUpdate,
    ShortMentorIn,
)
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.mentor import (
    get_all_mentors_use_case,
    get_archive_mentor_use_case,
    get_create_mentor_use_case,
    get_head_mentors_use_case,
    get_mentor_list_filters,
    get_mentor_use_case,
    get_recover_mentor_use_case,
    get_update_mentor_use_case,
)
from app.presentation.policies.mentors.can_archive_mentor import CanArchiveMentor
from app.presentation.policies.mentors.can_create_mentor import CanCreateMentor
from app.presentation.policies.mentors.can_edit_mentor import CanEditMentor
from app.presentation.policies.mentors.can_get_all_mentors import CanGetAllMentors
from app.presentation.policies.mentors.can_get_head_mentors import CanGetHeadMentors
from app.presentation.policies.mentors.can_get_mentor import CanGetMentor
from app.presentation.policies.mentors.can_recover_mentor import CanRecoverMentor

router = APIRouter(prefix="/mentor", tags=["mentor"])


@router.get("/me")
async def get_mentor_me(
    mentor: MentorProfile = Depends(get_current_employee),
) -> FullMentorOut:
    return FullMentorOut.model_validate(mentor)


@router.post("", response_model=MentorOut, status_code=HTTP_201_CREATED)
async def create_mentor(
    mentor_schema: ShortMentorIn,
    employee: Annotated[MentorProfile, Depends(CanCreateMentor())],
    use_case: CreateMentorUseCase = Depends(get_create_mentor_use_case),
) -> MentorOut:
    try:
        new_mentor = await use_case(mentor_schema, commit=True)
        logger.info(f"Mentor created: {new_mentor.id}")

        return new_mentor
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/head-mentors", response_model=ListResult[MentorOut])
async def get_head_mentors(
    employee: Annotated[MentorProfile, Depends(CanGetHeadMentors())],
    use_case: GetHeadMentorsUseCase = Depends(get_head_mentors_use_case),
) -> ListResult[MentorOut]:
    unit_id = employee.unit_id if employee.role in [Role.mentor] else None
    return await use_case(unit_id=unit_id)


@router.get("", response_model=MentorListResponse)
async def list_mentors(
    employee: Annotated[MentorProfile, Depends(CanGetAllMentors())],
    filters: MentorListFilters = Depends(get_mentor_list_filters),
    use_case: GetAllMentorsUseCase = Depends(get_all_mentors_use_case),
) -> MentorListResponse:
    result = await use_case(filters, employee=employee)

    return MentorListResponse(
        items=result.items,
        total=result.total,
        limit=filters.pagination.limit,
        offset=filters.pagination.offset,
    )


@router.get("/{mentor_id}", response_model=MentorOut)
async def get_mentor(
    mentor_id: UUID,
    _: Annotated[MentorProfile, Depends(CanGetMentor())],
    use_case: GetMentorUseCase = Depends(get_mentor_use_case),
) -> MentorOut:
    received_mentor = await use_case(mentor_id)
    if received_mentor is None:
        logger.warning(f"Mentor not found: {mentor_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")

    return received_mentor


@router.patch("/{mentor_id}", response_model=MentorOut)
async def update_mentor(
    mentor_id: UUID,
    mentor_update: MentorUpdate,
    _: Annotated[MentorProfile, Depends(CanEditMentor())],
    use_case: UpdateMentorUseCase = Depends(get_update_mentor_use_case),
) -> MentorOut:
    try:
        updated_mentor = await use_case(mentor_id, mentor_update, commit=True)

        if not updated_mentor:
            logger.warning(f"Mentor not found: {mentor_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")

        logger.info(f"Mentor updated: {mentor_id}")
        return updated_mentor
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{mentor_id}", response_model=MentorOut)
async def archive_mentor(
    mentor_id: UUID,
    _: Annotated[MentorProfile, Depends(CanArchiveMentor())],
    use_case: ArchiveMentorUseCase = Depends(get_archive_mentor_use_case),
) -> MentorOut:
    try:
        archived_mentor = await use_case(mentor_id, commit=True)
        if not archived_mentor:
            logger.warning(f"Mentor not found: {mentor_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")

        logger.info(f"Mentor archived: {mentor_id}")
        return archived_mentor
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{mentor_id}/recover", response_model=MentorOut)
async def recover_mentor(
    mentor_id: UUID,
    _: Annotated[MentorProfile, Depends(CanRecoverMentor())],
    use_case: RecoverMentorUseCase = Depends(get_recover_mentor_use_case),
) -> MentorOut:
    try:
        recovered_mentor = await use_case(mentor_id, commit=True)

        if not recovered_mentor:
            logger.warning(f"Mentor not found: {mentor_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Mentor not found")

        logger.info(f"Mentor recovered: {mentor_id}")
        return recovered_mentor

    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
