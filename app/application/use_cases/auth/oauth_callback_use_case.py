import json
from uuid import UUID

import jwt
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi_users.authentication import Strategy
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.jwt import decode_jwt
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token
from loguru import logger
from starlette.status import HTTP_302_FOUND

from app.config import config
from app.infrastructure.database import User
from app.presentation.auth_backend import auth_backend


class OAuthCallbackUseCase:
    def __init__(
        self,
        oauth_client: GoogleOAuth2,
        user_manager: BaseUserManager[User, UUID],
        strategy: Strategy[User, UUID],
    ):
        self._oauth_client = oauth_client
        self._user_manager = user_manager
        self._strategy = strategy

    async def __call__(
        self,
        request: Request,
        token: OAuth2Token,
        state: str,
    ) -> RedirectResponse:
        try:
            account_id, account_email = await self._oauth_client.get_id_email(token["access_token"])

            if account_email is None:
                logger.error("OAuth: email not available")
                return RedirectResponse(
                    url=f"{config.FRONTEND_REDIRECT_URI}?error={ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL}",
                    status_code=HTTP_302_FOUND,
                )

            try:
                decode_jwt(state, config.AUTH_SIGNATURE_SECRET, [config.STATE_TOKEN_AUDIENCE])
            except jwt.DecodeError:
                logger.error("OAuth: invalid state token")
                return RedirectResponse(
                    url=f"{config.FRONTEND_REDIRECT_URI}?error={ErrorCode.ACCESS_TOKEN_DECODE_ERROR}",
                    status_code=HTTP_302_FOUND,
                )
            except jwt.ExpiredSignatureError:
                logger.error("OAuth: expired state token")
                return RedirectResponse(
                    url=f"{config.FRONTEND_REDIRECT_URI}?error={ErrorCode.ACCESS_TOKEN_ALREADY_EXPIRED}",
                    status_code=HTTP_302_FOUND,
                )

            try:
                user = await self._user_manager.oauth_callback(
                    self._oauth_client.name,
                    token["access_token"],
                    account_id,
                    account_email,
                    token.get("expires_at"),
                    token.get("refresh_token"),
                    request,
                    associate_by_email=True,
                    is_verified_by_default=True,
                )
            except UserAlreadyExists:
                logger.error("OAuth: user already exists")
                return RedirectResponse(
                    url=f"{config.FRONTEND_REDIRECT_URI}?error={ErrorCode.OAUTH_USER_ALREADY_EXISTS}",
                    status_code=HTTP_302_FOUND,
                )

            if not user.is_active:
                logger.error(f"OAuth: user {user.id} is not active")
                return RedirectResponse(
                    url=f"{config.FRONTEND_REDIRECT_URI}?error={ErrorCode.LOGIN_BAD_CREDENTIALS}",
                    status_code=HTTP_302_FOUND,
                )

            response = await auth_backend.login(self._strategy, user)
            await self._user_manager.on_after_login(user, request, response)

            access_token = None
            if hasattr(response, "body"):
                try:
                    body = response.body.decode() if isinstance(response.body, (bytes, bytearray)) else response.body
                    data = json.loads(body)
                    access_token = data.get("access_token")
                except Exception:
                    pass

            if not access_token:
                access_token = await self._strategy.write_token(user)

            logger.info(f"OAuth callback successful for user {user.id}, redirecting to frontend")

            return RedirectResponse(
                url=f"{config.FRONTEND_REDIRECT_URI}?access_token={access_token}",
                status_code=HTTP_302_FOUND,
            )

        except Exception as e:
            logger.error("OAuth callback error", exc_info=True)
            msg = str(e).replace(" ", "%20").replace("&", "%26").replace("?", "%3F")
            return RedirectResponse(
                url=f"{config.FRONTEND_REDIRECT_URI}?error={msg}",
                status_code=HTTP_302_FOUND,
            )
