from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, Query

from app.application.use_cases.mentors.archive_mentor_use_case import ArchiveMentorUseCase
from app.application.use_cases.mentors.create_mentor_use_case import CreateMentorUseCase
from app.application.use_cases.mentors.get_all_mentors_use_case import GetAllMentorsUseCase
from app.application.use_cases.mentors.get_head_mentors_use_case import GetHeadMentorsUseCase
from app.application.use_cases.mentors.get_mentor_use_case import GetMentorUseCase
from app.application.use_cases.mentors.recover_mentor_use_case import RecoverMentorUseCase
from app.application.use_cases.mentors.update_mentor_use_case import UpdateMentorUseCase
from app.common.pagination import Pagination
from app.domain.entities.employee.enum import Role, MentorSort
from app.domain.entities.employee.mentor import MentorListFilters, Order
from app.domain.unit_of_work import IUnitOfWork
from app.presentation.dependencies.unit_of_work import get_unit_of_work


def get_create_mentor_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> CreateMentorUseCase:
    return CreateMentorUseCase(uow)


def get_mentor_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetMentorUseCase:
    return GetMentorUseCase(uow)


def get_all_mentors_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetAllMentorsUseCase:
    return GetAllMentorsUseCase(uow)


def get_update_mentor_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> UpdateMentorUseCase:
    return UpdateMentorUseCase(uow)


def get_archive_mentor_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> ArchiveMentorUseCase:
    return ArchiveMentorUseCase(uow)


def get_recover_mentor_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> RecoverMentorUseCase:
    return RecoverMentorUseCase(uow)


def get_head_mentors_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetHeadMentorsUseCase:
    return GetHeadMentorsUseCase(uow)


def get_mentor_list_filters(
    search: str | None = Query(default=None),
    available: bool | None = Query(default=None),
    available_for_interview: bool | None = Query(default=None),
    role: list[Role] | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
    order_by: MentorSort = Query(default=MentorSort.full_name),
    order_dir: Literal["asc", "desc"] = Query(default="asc"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> MentorListFilters:
    return MentorListFilters(
        search=search,
        available=available,
        available_for_interview=available_for_interview,
        role=role,
        unit_id=unit_id,
        order=Order(by=order_by, direction=order_dir),
        pagination=Pagination(limit=limit, offset=offset),
    )
