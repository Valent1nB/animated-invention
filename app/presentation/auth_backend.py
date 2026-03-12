import uuid
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    UUIDIDMixin,
    models,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.mentors.register_mentor_oauth_use_case import RegisterMentorOauthUseCase
from app.config import config
from app.infrastructure.database import User
from app.infrastructure.database.models.auth import get_user_db
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.dependencies.db import get_async_session
from app.presentation.http_bearer_transport import HTTPBearerTransport

SECRET = config.AUTH_SIGNATURE_SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def __init__(self, user_db: SQLAlchemyUserDatabase, session: AsyncSession):
        super().__init__(user_db)
        self._session = session

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.info(f"User {user.id} has registered.")

        async with UnitOfWork(existing_session=self._session) as uow:
            try:
                use_case = RegisterMentorOauthUseCase(uow)
                await use_case(user)
                await uow.commit()
            except Exception as e:
                logger.error(f"Failed to execute on_after_register for user {user.id}: {e}")
                await uow.rollback()
                await self.user_db.delete(user)
                raise


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
    session: AsyncSession = Depends(get_async_session),
):
    yield UserManager(user_db=user_db, session=session)


http_bearer_transport = HTTPBearerTransport()


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, token_audience=["px:auth"], lifetime_seconds=config.JWT_ACCESS_LIFETIME)


def get_jwt_refresh_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, token_audience=["px:refresh"], lifetime_seconds=config.JWT_REFRESH_LIFETIME)


auth_backend: AuthenticationBackend[User, UUID] = AuthenticationBackend(
    name="jwt",
    transport=http_bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

google_oauth_client = GoogleOAuth2(config.GOOGLE_OAUTH_CLIENT_ID, config.GOOGLE_OAUTH_CLIENT_SECRET)
