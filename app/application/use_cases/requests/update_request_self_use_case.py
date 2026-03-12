from uuid import UUID

from app.domain.entities.request.request import RequestOut, RequestUpdateSelf
from app.domain.unit_of_work import IUnitOfWork


class UpdateRequestSelfUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, request_id: UUID, requester_id: UUID, request_update: RequestUpdateSelf, commit: bool = False
    ) -> RequestOut | None:
        updated_request = await self._uow.requests.update_self(request_id, requester_id, request_update)
        if commit:
            await self._uow.commit()

        return updated_request
