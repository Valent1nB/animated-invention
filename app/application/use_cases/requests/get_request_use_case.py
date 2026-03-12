from uuid import UUID

from app.domain.entities.request.request import RequestOut
from app.domain.unit_of_work import IUnitOfWork


class GetRequestUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, request_id: UUID) -> RequestOut | None:
        return await self._uow.requests.get_one(request_id)
