from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, HTTPException, Query
from starlette.status import HTTP_403_FORBIDDEN

from app.application.use_cases.interns.create_intern_use_case import CreateInternUseCase
from app.application.use_cases.interns.get_all_interns_use_case import GetAllInternsUseCase
from app.application.use_cases.interns.get_intern_snapshot_use_case import GetInternSnapshotUseCase
from app.application.use_cases.interns.get_intern_stats_comparison_use_case import (
    GetInternStatsComparisonUseCase,
)
from app.application.use_cases.interns.get_intern_stats_use_case import GetInternStatsUseCase
from app.application.use_cases.interns.get_intern_use_case import GetInternUseCase
from app.application.use_cases.interns.get_interns_grouped_by_mentor_use_case import (
    GetInternsGroupedByMentorUseCase,
)
from app.application.use_cases.interns.reassign_mentor_use_case import ReassignMentorUseCase
from app.application.use_cases.interns.update_intern_use_case import UpdateInternUseCase
from app.common.pagination import Pagination
from app.domain.entities.employee.enum import (
    EmploymentStatus,
    EnglishLevel,
    InternshipStatus,
    InternSort,
    MilitaryStatus,
    UserRole,
)
from app.domain.entities.employee.intern import (
    DateRange,
    InternListFilters,
    InternSnapshotFilters,
    InternStatsComparisonFilters,
    InternStatsFilters,
    InternUpdate,
    InternUpdateMentor,
    Order,
)
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.employee import get_current_employee
from app.presentation.dependencies.unit_of_work import get_unit_of_work


def get_create_intern_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> CreateInternUseCase:
    return CreateInternUseCase(uow)


def get_intern_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetInternUseCase:
    return GetInternUseCase(uow)


def get_all_interns_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetAllInternsUseCase:
    return GetAllInternsUseCase(uow)


def get_intern_stats_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetInternStatsUseCase:
    return GetInternStatsUseCase(uow)


def get_intern_snapshot_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetInternSnapshotUseCase:
    return GetInternSnapshotUseCase(uow)


def get_intern_stats_comparison_use_case(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> GetInternStatsComparisonUseCase:
    return GetInternStatsComparisonUseCase(uow)


def get_update_intern_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> UpdateInternUseCase:
    return UpdateInternUseCase(uow)


def get_reassign_mentor_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> ReassignMentorUseCase:
    return ReassignMentorUseCase(uow)


def get_interns_grouped_by_mentors_use_case(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> GetInternsGroupedByMentorUseCase:
    return GetInternsGroupedByMentorUseCase(uow)


def get_intern_list_filters(
    search: str | None = Query(default=None),
    status: list[InternshipStatus] | None = Query(default=None),
    mentor_id: UUID | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
    employment_status: list[EmploymentStatus] | None = Query(default=None),
    english_level: list[EnglishLevel] | None = Query(default=None),
    ready_for_sale: bool | None = Query(default=None),
    military_status: list[MilitaryStatus] | None = Query(default=None),
    order_by: InternSort = Query(default=InternSort.full_name),
    order_dir: Literal["asc", "desc"] = Query(default="asc"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> InternListFilters:
    return InternListFilters(
        search=search,
        status=status,
        mentor_id=mentor_id,
        unit_id=unit_id,
        employment_status=employment_status,
        english_level=english_level,
        ready_for_sale=ready_for_sale,
        military_status=military_status,
        order=Order(by=order_by, direction=order_dir),
        pagination=Pagination(limit=limit, offset=offset),
    )


def get_historical_intern_stats_filters(
    statuses: list[InternshipStatus] = Query(default_factory=list, description="Allowed: sold, laid_off"),
    start_date: date = Query(..., description="Start of the period (inclusive)"),
    end_date: date = Query(..., description="End of the period (inclusive)"),
    mentor_id: UUID | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
) -> InternStatsFilters:
    return InternStatsFilters(
        statuses=set(statuses) if statuses else None,
        period=DateRange(start_date=start_date, end_date=end_date),
        mentor_id=mentor_id,
        unit_id=unit_id,
    )


def get_intern_snapshot_filters(
    statuses: list[InternshipStatus] = Query(default_factory=list),
    english_levels: list[EnglishLevel] = Query(default_factory=list),
    cities: list[str] = Query(default_factory=list),
    ready_for_sale: bool | None = Query(default=None),
    mentor_id: UUID | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
) -> InternSnapshotFilters:
    return InternSnapshotFilters(
        statuses=set(statuses) if statuses else None,
        english_levels=set(english_levels) if english_levels else None,
        cities=set(cities) if cities else None,
        ready_for_sale=ready_for_sale,
        mentor_id=mentor_id,
        unit_id=unit_id,
    )


def get_intern_stats_comparison_filters(
    statuses: list[InternshipStatus] = Query(default_factory=list, description="Allowed: sold, laid_off"),
    current_start_date: date = Query(..., description="Current period start (inclusive)"),
    current_end_date: date = Query(..., description="Current period end (inclusive)"),
    previous_start_date: date = Query(..., description="Previous period start (inclusive)"),
    previous_end_date: date = Query(..., description="Previous period end (inclusive)"),
    mentor_id: UUID | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
) -> InternStatsComparisonFilters:
    current_period = DateRange(start_date=current_start_date, end_date=current_end_date)
    previous_period = DateRange(start_date=previous_start_date, end_date=previous_end_date)

    return InternStatsComparisonFilters(
        statuses=set(statuses) if statuses else None,
        current_period=current_period,
        previous_period=previous_period,
        mentor_id=mentor_id,
        unit_id=unit_id,
    )


async def sanitize_intern_update(
    employee: Annotated[MentorProfile, Depends(get_current_employee)],
    payload: InternUpdate,
) -> InternUpdate | InternUpdateMentor:
    if employee.role in {UserRole.superuser, UserRole.head_mentor}:
        return payload

    try:
        data = payload.model_dump(exclude_unset=True)
        return InternUpdateMentor(**data)

    except Exception:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not allowed to update some of these fields",
        )
