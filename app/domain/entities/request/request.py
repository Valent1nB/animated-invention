from datetime import datetime
from typing import Literal, Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.pagination import Pagination
from app.domain.entities.employee.employee import ShortEmployeeOut
from app.domain.entities.employee.enum import RequestSort, RequestStatus, RequestTopic
from app.domain.entities.employee.mentor import ShortMentorOut


class RequestOut(BaseModel):
    id: UUID
    requester: ShortMentorOut
    receiver: ShortMentorOut
    status: RequestStatus
    topic: RequestTopic
    intern: ShortEmployeeOut | None = None
    extra_info: str
    comment_from_receiver: str
    closed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequestCountOut(BaseModel):
    count: int


class RequestIn(BaseModel):
    receiver_id: UUID
    topic: RequestTopic
    intern_id: UUID | None = None
    extra_info: str = ""

    model_config = ConfigDict(extra="forbid")


class RequestUpdate(BaseModel):
    status: RequestStatus | None = None
    comment_from_receiver: str | None = None

    model_config = ConfigDict(extra="forbid")


class RequestUpdateSelf(BaseModel):
    extra_info: str | None = None

    model_config = ConfigDict(extra="forbid")


class Order(BaseModel):
    by: RequestSort = RequestSort.created_at
    direction: Literal["asc", "desc"] = "desc"


class RequestListFilters(BaseModel):
    status: RequestStatus | None = None
    topic: RequestTopic | None = None
    requester_id: UUID | None = None
    receiver_id: UUID | None = None
    unit_id: UUID | None = None
    order: Order = Order()
    pagination: Pagination = Pagination()


class RequestListResponse(BaseModel):
    items: Sequence[RequestOut]
    total: int
    limit: int
    offset: int
