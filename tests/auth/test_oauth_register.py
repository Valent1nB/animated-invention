from unittest.mock import patch

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_302_FOUND, HTTP_403_FORBIDDEN

from app.application.use_cases.mentors.register_mentor_oauth_use_case import RegisterMentorOauthUseCase
from app.infrastructure.unit_of_work import UnitOfWork


@pytest.mark.asyncio
async def test_oauth_register_with_existing_mentor(
    async_session: AsyncSession,
    test_mentor_for_intern_auth,
    user_for_mentor_email,
):
    async with UnitOfWork(existing_session=async_session) as uow:
        use_case = RegisterMentorOauthUseCase(uow)
        await use_case(user_for_mentor_email, commit=True)

    await async_session.refresh(test_mentor_for_intern_auth)
    assert test_mentor_for_intern_auth.user_id == user_for_mentor_email.id


@pytest.mark.asyncio
async def test_oauth_register_without_mentor(async_session: AsyncSession, user_with_new_email):
    async with UnitOfWork(existing_session=async_session) as uow:
        use_case = RegisterMentorOauthUseCase(uow)
        with pytest.raises(Exception):
            await use_case(user_with_new_email, commit=True)


@pytest.mark.asyncio
async def test_oauth_register_mentor_not_found(async_session: AsyncSession, user_with_nonexistent_email):
    async with UnitOfWork(existing_session=async_session) as uow:
        use_case = RegisterMentorOauthUseCase(uow)
        with pytest.raises(HTTPException) as exc_info:
            await use_case(user_with_nonexistent_email, commit=True)

        assert exc_info.value.status_code == HTTP_403_FORBIDDEN
        assert "Mentor is not registered" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_oauth_register_mentor_already_attached(
    async_session: AsyncSession,
    test_mentor_for_intern_auth,
    user_for_mentor_email,
):
    print(test_mentor_for_intern_auth)
    print(user_for_mentor_email)
    async with UnitOfWork(existing_session=async_session) as uow:
        use_case = RegisterMentorOauthUseCase(uow)
        await use_case(user_for_mentor_email, commit=True)

    await async_session.refresh(test_mentor_for_intern_auth)
    assert test_mentor_for_intern_auth.user_id == user_for_mentor_email.id


@pytest.mark.asyncio
@patch("fastapi_users.router.oauth.decode_jwt")
@patch("httpx_oauth.clients.google.GoogleOAuth2.get_access_token")
@patch("httpx_oauth.clients.google.GoogleOAuth2.get_id_email")
async def test_oauth_callback_success_with_existing_mentor(
    mock_get_id_email,
    mock_get_access_token,
    mock_decode_jwt,
    async_session: AsyncSession,
    test_mentor_for_intern_auth_no_user,
    unauthorized_client: AsyncClient,
    mock_oauth_token,
):
    mock_decode_jwt.return_value = {"state": "test_state"}
    mock_get_access_token.return_value = mock_oauth_token
    mock_get_id_email.return_value = ("google_id", test_mentor_for_intern_auth_no_user.email)

    response = await unauthorized_client.get("/api/v1/auth/google/callback?code=test_code&state=test_state")

    assert response.status_code == HTTP_302_FOUND
