from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.application.use_cases.requests.create_request_use_case import CreateRequestUseCase
from app.application.use_cases.requests.get_all_requests_use_case import GetAllRequestsUseCase
from app.application.use_cases.requests.get_request_use_case import GetRequestUseCase
from app.application.use_cases.requests.update_request_self_use_case import UpdateRequestSelfUseCase
from app.application.use_cases.requests.update_request_use_case import UpdateRequestUseCase
from app.common.pagination import Pagination
from app.domain.entities.employee.enum import RequestStatus
from app.domain.entities.request.request import (
    RequestCountOut,
    RequestIn,
    RequestListFilters,
    RequestListResponse,
    RequestOut,
    RequestUpdate,
    RequestUpdateSelf,
)
from app.infrastructure.database import MentorProfile
from app.presentation.dependencies.request import (
    get_all_requests_use_case,
    get_create_request_use_case,
    get_request_list_filters,
    get_request_use_case,
    get_update_request_self_use_case,
    get_update_request_use_case,
)
from app.presentation.policies.requests.can_create_request import CanCreateRequest
from app.presentation.policies.requests.can_get_all_requests import CanGetAllRequests
from app.presentation.policies.requests.can_get_request import CanGetRequest
from app.presentation.policies.requests.can_update_request import CanUpdateRequest
from app.presentation.policies.requests.can_update_request_self import CanUpdateRequestSelf

router = APIRouter(prefix="/request", tags=["request"])


@router.patch("/{request_id}/self", response_model=RequestOut)
async def update_request_self(
    request_id: UUID,
    request_update: RequestUpdateSelf,
    employee: Annotated[MentorProfile, Depends(CanUpdateRequestSelf())],
    use_case: UpdateRequestSelfUseCase = Depends(get_update_request_self_use_case),
) -> RequestOut:
    try:
        updated_request = await use_case(request_id, employee.id, request_update, commit=True)

        if not updated_request:
            logger.warning(f"Request not found or cannot be updated: {request_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Request not found or cannot be updated")

        logger.info(f"Request updated by requester: {request_id}")
        return updated_request
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("", response_model=RequestOut, status_code=HTTP_201_CREATED)
async def create_request(
    request_schema: RequestIn,
    employee: Annotated[MentorProfile, Depends(CanCreateRequest())],
    use_case: CreateRequestUseCase = Depends(get_create_request_use_case),
) -> RequestOut:
    try:
        new_request = await use_case(request_schema, employee.id, commit=True)
        logger.info(f"Request created: {new_request.id} by {employee.id}")

        return new_request
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/count/new")
async def get_new_requests_count(
    employee: Annotated[MentorProfile, Depends(CanGetAllRequests())],
    filters: RequestListFilters = Depends(get_request_list_filters),
    use_case: GetAllRequestsUseCase = Depends(get_all_requests_use_case),
) -> RequestCountOut:
    count_filters = RequestListFilters(
        status=RequestStatus.created,
        topic=filters.topic,
        requester_id=filters.requester_id,
        receiver_id=filters.receiver_id,
        unit_id=filters.unit_id,
        order=filters.order,
        pagination=Pagination(limit=1, offset=0),
    )
    result = await use_case(count_filters, employee=employee)
    return RequestCountOut(count=result.total)


@router.get("", response_model=RequestListResponse)
async def list_requests(
    employee: Annotated[MentorProfile, Depends(CanGetAllRequests())],
    filters: RequestListFilters = Depends(get_request_list_filters),
    use_case: GetAllRequestsUseCase = Depends(get_all_requests_use_case),
) -> RequestListResponse:
    result = await use_case(filters, employee=employee)

    return RequestListResponse(
        items=result.items,
        total=result.total,
        limit=filters.pagination.limit,
        offset=filters.pagination.offset,
    )


@router.get("/{request_id}", response_model=RequestOut)
async def get_request(
    request_id: UUID,
    _: Annotated[MentorProfile, Depends(CanGetRequest())],
    use_case: GetRequestUseCase = Depends(get_request_use_case),
) -> RequestOut:
    received_request = await use_case(request_id)
    if received_request is None:
        logger.warning(f"Request not found: {request_id}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Request not found")

    return received_request


@router.patch("/{request_id}", response_model=RequestOut)
async def update_request(
    request_id: UUID,
    request_update: RequestUpdate,
    _: Annotated[MentorProfile, Depends(CanUpdateRequest())],
    use_case: UpdateRequestUseCase = Depends(get_update_request_use_case),
) -> RequestOut:
    try:
        updated_request = await use_case(request_id, request_update, commit=True)

        if not updated_request:
            logger.warning(f"Request not found: {request_id}")
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Request not found")

        logger.info(f"Request updated: {request_id}")
        return updated_request
    except SQLAlchemyError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
