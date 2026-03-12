from uuid import UUID

from app.domain.entities.request.request import RequestIn, RequestOut
from app.domain.unit_of_work import IUnitOfWork


class CreateRequestUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, request: RequestIn, requester_id: UUID, commit: bool = False) -> RequestOut:
        created_request = await self._uow.requests.create(request, requester_id)
        if commit:
            await self._uow.commit()

        return created_request
