from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

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
from app.domain.entities.employee.intern import (
    InternGroupedByMentorResponse,
    InternIn,
    InternListFilters,
    InternListResponse,
    InternOut,
    InternSnapshotFilters,
    InternStatsComparisonFilters,
    InternStatsComparisonOut,
    InternStatsFilters,
    InternStatsOut,
    InternUpdate,
    ReassignMentorRequest,
)
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.intern import (
    get_all_interns_use_case,
    get_create_intern_use_case,
    get_historical_intern_stats_filters,
    get_intern_list_filters,
    get_intern_snapshot_filters,
    get_intern_snapshot_use_case,
    get_intern_stats_comparison_filters,
    get_intern_stats_comparison_use_case,
    get_intern_stats_use_case,
    get_intern_use_case,
    get_interns_grouped_by_mentors_use_case,
    get_reassign_mentor_use_case,
    get_update_intern_use_case,
    sanitize_intern_update,
)
from app.presentation.policies.interns.can_create_intern import CanCreateIntern
from app.presentation.policies.interns.can_edit_intern import CanEditIntern
from app.presentation.policies.interns.can_get_all_interns import CanGetAllInterns
from app.presentation.policies.interns.can_get_intern import CanGetIntern
from app.presentation.policies.interns.can_get_intern_stats import (
    CanCompareInternStats,
    CanGetInternSnapshotStats,
    CanGetInternStats,
)
from app.presentation.policies.interns.can_get_interns_grouped_by_mentor import CanGetInternsGroupedByMentor
from app.presentation.policies.interns.can_reassign_mentor import CanReassignMentor

router = APIRouter(prefix="/intern", tags=["intern"])


@router.get("/stats", response_model=InternStatsOut)
async def get_intern_stats(
    employee: Annotated[MentorProfile, Depends(CanGetInternStats())],
    filters: InternStatsFilters = Depends(get_historical_intern_stats_filters),
    use_case: GetInternStatsUseCase = Depends(get_intern_stats_use_case),
) -> InternStatsOut:
    return await use_case(filters, employee=employee)


@router.get("/stats/current", response_model=InternStatsOut)
async def get_intern_snapshot_stats(
    employee: Annotated[MentorProfile, Depends(CanGetInternSnapshotStats())],
    filters: InternSnapshotFilters = Depends(get_intern_snapshot_filters),
    use_case: GetInternSnapshotUseCase = Depends(get_intern_snapshot_use_case),
) -> InternStatsOut:
    return await use_case(filters, employee=employee)


@router.get("/stats/comparison", response_model=InternStatsComparisonOut)
async def compare_intern_stats(
    employee: Annotated[MentorProfile, Depends(CanCompareInternStats())],
    filters: InternStatsComparisonFilters = Depends(get_intern_stats_comparison_filters),
    use_case: GetInternStatsComparisonUseCase = Depends(get_intern_stats_comparison_use_case),
) -> InternStatsComparisonOut:
    return await use_case(filters, employee=employee)


@router.get("/grouped-by-mentor", response_model=InternGroupedByMentorResponse)
async def get_interns_grouped_by_mentor(
    employee: Annotated[MentorProfile, Depends(CanGetInternsGroupedByMentor())],
    filters: InternListFilters = Depends(get_intern_list_filters),
    use_case: GetInternsGroupedByMentorUseCase = Depends(get_interns_grouped_by_mentors_use_case),
) -> InternGroupedByMentorResponse:
    return await use_case(filters, employee=employee)


@router.post("", response_model=InternOut, status_code=HTTP_201_CREATED)
async def create_intern(
    intern_schema: InternIn,
    _: Annotated[MentorProfile, Depends(CanCreateIntern())],
    use_case: CreateInternUseCase = Depends(get_create_intern_use_case),
) -> InternOut:
    try:
        new_intern = await use_case(intern_schema, commit=True)
        logger.info(f"Intern created: {new_intern.id}")

        return new_intern
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{intern_id}", response_model=InternOut)
async def get_intern(
    intern_id: UUID,
    _: Annotated[MentorProfile, Depends(CanGetIntern())],
    use_case: GetInternUseCase = Depends(get_intern_use_case),
) -> InternOut:
    received_intern = await use_case(intern_id)
    if received_intern is None:
        logger.warning(f"Intern not found: {intern_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")

    return received_intern


@router.get("", response_model=InternListResponse)
async def get_all_interns(
    employee: Annotated[MentorProfile, Depends(CanGetAllInterns())],
    filters: InternListFilters = Depends(get_intern_list_filters),
    use_case: GetAllInternsUseCase = Depends(get_all_interns_use_case),
) -> InternListResponse:
    result = await use_case(filters, employee=employee)

    return InternListResponse(
        items=result.items,
        total=result.total,
        limit=filters.pagination.limit,
        offset=filters.pagination.offset,
    )


@router.patch("/{intern_id}", response_model=InternOut)
async def update_intern(
    intern_id: UUID,
    intern_update: Annotated[InternUpdate, Depends(sanitize_intern_update)],
    _: Annotated[MentorProfile, Depends(CanEditIntern())],
    use_case: UpdateInternUseCase = Depends(get_update_intern_use_case),
) -> InternOut:
    try:
        updated_intern = await use_case(intern_id, intern_update, commit=True)

        if not updated_intern:
            logger.warning(f"Intern not found: {intern_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")

        logger.info(f"Intern updated: {intern_id}")
        return updated_intern
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{intern_id}/reassign-mentor", response_model=InternOut)
async def reassign_mentor(
    intern_id: UUID,
    request: ReassignMentorRequest,
    _: Annotated[MentorProfile, Depends(CanReassignMentor())],
    use_case: ReassignMentorUseCase = Depends(get_reassign_mentor_use_case),
) -> InternOut:
    try:
        updated_intern = await use_case(intern_id, request.new_mentor_id, commit=True)

        if not updated_intern:
            logger.warning(f"Intern not found: {intern_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Intern not found")

        logger.info(f"Intern mentor reassigned: {intern_id}")
        return updated_intern

    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
