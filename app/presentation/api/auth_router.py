from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2Token

from app.application.use_cases.auth.oauth_authorize_use_case import OAuthAuthorizeUseCase
from app.application.use_cases.auth.oauth_callback_use_case import OAuthCallbackUseCase
from app.config import config
from app.presentation.auth_backend import google_oauth_client
from app.presentation.dependencies.auth import (
    get_oauth_authorize_use_case,
    get_oauth_callback_use_case,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/authorize")
async def google_authorize(
    scopes: list[str] = Query(None),
    use_case: OAuthAuthorizeUseCase = Depends(get_oauth_authorize_use_case),
) -> dict[str, str]:
    return await use_case(scopes)


@router.get("/google/callback", name="google_oauth_callback")
async def google_callback(
    request: Request,
    access_token_state: tuple[OAuth2Token, str] = Depends(
        OAuth2AuthorizeCallback(
            google_oauth_client,
            redirect_url=config.GOOGLE_REDIRECT_URI,
        )
    ),
    use_case: OAuthCallbackUseCase = Depends(get_oauth_callback_use_case),
) -> RedirectResponse:
    token, state = access_token_state
    return await use_case(request, token, state)
