from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, Query

from app.application.use_cases.requests.create_request_use_case import CreateRequestUseCase
from app.application.use_cases.requests.get_all_requests_use_case import GetAllRequestsUseCase
from app.application.use_cases.requests.get_request_use_case import GetRequestUseCase
from app.application.use_cases.requests.update_request_self_use_case import UpdateRequestSelfUseCase
from app.application.use_cases.requests.update_request_use_case import UpdateRequestUseCase
from app.common.pagination import Pagination
from app.domain.entities.employee.enum import RequestSort, RequestStatus, RequestTopic
from app.domain.entities.request.request import Order, RequestListFilters
from app.domain.unit_of_work import IUnitOfWork
from app.presentation.dependencies.unit_of_work import get_unit_of_work


def get_create_request_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> CreateRequestUseCase:
    return CreateRequestUseCase(uow)


def get_request_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetRequestUseCase:
    return GetRequestUseCase(uow)


def get_all_requests_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> GetAllRequestsUseCase:
    return GetAllRequestsUseCase(uow)


def get_update_request_use_case(uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)]) -> UpdateRequestUseCase:
    return UpdateRequestUseCase(uow)


def get_update_request_self_use_case(
    uow: Annotated[IUnitOfWork, Depends(get_unit_of_work)],
) -> UpdateRequestSelfUseCase:
    return UpdateRequestSelfUseCase(uow)


def get_request_list_filters(
    status: RequestStatus | None = Query(default=None),
    topic: RequestTopic | None = Query(default=None),
    requester_id: UUID | None = Query(default=None),
    receiver_id: UUID | None = Query(default=None),
    unit_id: UUID | None = Query(default=None),
    order_by: RequestSort = Query(default=RequestSort.created_at),
    order_dir: Literal["asc", "desc"] = Query(default="desc"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> RequestListFilters:
    return RequestListFilters(
        status=status,
        topic=topic,
        requester_id=requester_id,
        receiver_id=receiver_id,
        unit_id=unit_id,
        order=Order(by=order_by, direction=order_dir),
        pagination=Pagination(limit=limit, offset=offset),
    )
