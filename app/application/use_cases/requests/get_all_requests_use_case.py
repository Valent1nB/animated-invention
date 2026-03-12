from app.common.list import ListResult
from app.domain.entities.request.request import RequestListFilters, RequestOut
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetAllRequestsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, filters: RequestListFilters, employee: MentorProfile | None = None
    ) -> ListResult[RequestOut]:
        return await self._uow.requests.list(filters, employee=employee)
