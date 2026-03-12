from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi_users.authentication import Strategy
from fastapi_users.manager import BaseUserManager

from app.application.use_cases.auth.oauth_authorize_use_case import OAuthAuthorizeUseCase
from app.application.use_cases.auth.oauth_callback_use_case import OAuthCallbackUseCase
from app.infrastructure.database import User
from app.presentation.auth_backend import (
    auth_backend,
    get_user_manager,
    google_oauth_client,
)


def get_oauth_authorize_use_case() -> OAuthAuthorizeUseCase:
    return OAuthAuthorizeUseCase(google_oauth_client)


def get_oauth_callback_use_case(
    user_manager: Annotated[BaseUserManager[User, UUID], Depends(get_user_manager)],
    strategy: Annotated[Strategy[User, UUID], Depends(auth_backend.get_strategy)],
) -> OAuthCallbackUseCase:
    return OAuthCallbackUseCase(
        oauth_client=google_oauth_client,
        user_manager=user_manager,
        strategy=strategy,
    )
