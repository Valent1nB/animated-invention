from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.domain.repositories.media_repository import IMediaRepository
from app.domain.unit_of_work import IUnitOfWork


class RemoveAvatarUseCase:
    def __init__(self, uow: IUnitOfWork, media_repo: IMediaRepository):
        self._uow = uow
        self._media_repo = media_repo

    async def __call__(self, employee_id: UUID, commit: bool = False) -> None:
        # Try to find as mentor first
        mentor = await self._uow.mentors.get_one(employee_id)
        if mentor:
            if mentor.avatar_key:
                self._media_repo.delete(key=mentor.avatar_key)
                await self._uow.mentors.remove_avatar(employee_id)
                if commit:
                    await self._uow.commit()
            return

        # Try to find as intern
        intern = await self._uow.interns.get_one(employee_id)
        if intern:
            if intern.avatar_key:
                self._media_repo.delete(key=intern.avatar_key)
                await self._uow.interns.remove_avatar(employee_id)
                if commit:
                    await self._uow.commit()
            return

        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Employee not found")
