from fastapi import HTTPException
from loguru import logger
from starlette.status import HTTP_403_FORBIDDEN

from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import User


class RegisterMentorOauthUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, user: User, commit: bool = False):
        try:
            existing_mentor = await self._uow.mentors.get_one_by_email(user.email)
            if existing_mentor:
                await self._uow.mentors.attach_to_user(user_id=user.id, mentor_id=existing_mentor.id)
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Mentor is not registered")

            logger.info(f"User created for mentor {existing_mentor.id}")

            if commit:
                await self._uow.commit()

        except Exception as e:
            logger.error(f"Failed to create employee for user {user.id}: {e}")
            if commit:
                await self._uow.rollback()
            raise e
