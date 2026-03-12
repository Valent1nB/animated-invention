from tempfile import SpooledTemporaryFile
from typing import BinaryIO, Union
from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.domain.entities.employee.intern import InternOut
from app.domain.entities.employee.mentor import MentorOut
from app.domain.repositories.media_repository import IMediaRepository
from app.domain.unit_of_work import IUnitOfWork


class UploadAvatarUseCase:
    def __init__(self, uow: IUnitOfWork, media_repo: IMediaRepository):
        self._uow = uow
        self._media_repo = media_repo

    async def __call__(
        self,
        employee_id: UUID,
        file_key: str,
        file_content: str | BinaryIO | SpooledTemporaryFile,
        commit: bool = False,
    ) -> Union[MentorOut, InternOut]:
        try:
            avatar_key = self._media_repo.upload(file=file_content, key=file_key)
        except ValueError as e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

        try:
            # Try to find as mentor first
            mentor = await self._uow.mentors.get_one(employee_id)
            if mentor:
                updated_mentor = await self._uow.mentors.upload_avatar(employee_id, avatar_key)
                if commit:
                    await self._uow.commit()
                return MentorOut.model_validate(updated_mentor)

            # Try to find as intern
            intern = await self._uow.interns.get_one(employee_id)
            if intern:
                updated_intern = await self._uow.interns.upload_avatar(employee_id, avatar_key)
                if commit:
                    await self._uow.commit()
                return InternOut.model_validate(updated_intern)

            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Employee not found")
        except Exception as e:
            self._media_repo.delete(key=avatar_key)
            raise e
