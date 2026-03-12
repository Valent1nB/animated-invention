from fastapi_users.jwt import generate_jwt
from httpx_oauth.clients.google import GoogleOAuth2

from app.config import config


class OAuthAuthorizeUseCase:
    def __init__(self, oauth_client: GoogleOAuth2):
        self._oauth_client = oauth_client

    async def __call__(self, scopes: list[str] | None = None) -> dict[str, str]:
        state = generate_jwt(
            {"aud": config.STATE_TOKEN_AUDIENCE},
            config.AUTH_SIGNATURE_SECRET,
            3600,
        )

        authorization_url = await self._oauth_client.get_authorization_url(
            config.GOOGLE_REDIRECT_URI,
            state,
            scopes,
        )

        return {"authorization_url": authorization_url}
