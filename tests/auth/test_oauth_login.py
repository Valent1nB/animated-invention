from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_302_FOUND


@pytest.mark.asyncio
@patch("fastapi_users.router.oauth.decode_jwt")
@patch("httpx_oauth.clients.google.GoogleOAuth2.get_access_token")
@patch("httpx_oauth.clients.google.GoogleOAuth2.get_id_email")
async def test_oauth_login_existing_user(
    mock_get_id_email,
    mock_get_access_token,
    mock_decode_jwt,
    async_session: AsyncSession,
    test_mentor_for_intern_auth,
    unauthorized_client: AsyncClient,
    mock_oauth_token,
):
    mock_decode_jwt.return_value = {"state": "test_state"}
    mock_get_access_token.return_value = mock_oauth_token
    mock_get_id_email.return_value = ("google_id", test_mentor_for_intern_auth.email)

    response = await unauthorized_client.get("/api/v1/auth/google/callback?code=test_code&state=test_state")

    assert response.status_code == HTTP_302_FOUND


@pytest.mark.asyncio
@patch("httpx_oauth.clients.google.GoogleOAuth2.get_authorization_url")
async def test_oauth_login_authorize_flow(mock_get_authorization_url, unauthorized_client: AsyncClient):
    mock_get_authorization_url.return_value = "https://accounts.google.com/authorize?test"

    response = await unauthorized_client.get("/api/v1/auth/google/authorize")

    assert response.status_code == HTTP_200_OK
    assert response.json()["authorization_url"] == "https://accounts.google.com/authorize?test"
