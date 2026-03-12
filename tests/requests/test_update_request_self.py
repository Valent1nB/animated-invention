from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.domain.entities.employee.enum import RequestStatus
from app.infrastructure.database import MentorProfile as MentorProfileORM
from tests.factories.request import RequestFactory


@pytest.mark.asyncio
async def test_update_request_self_as_mentor_own_request(
    mentor_client: AsyncClient, async_session: AsyncSession, test_head_mentor_for_request
):
    result = await async_session.execute(select(MentorProfileORM).where(MentorProfileORM.email == "mentor@example.com"))
    mentor = result.scalar_one()

    request = RequestFactory(requester=mentor, receiver=test_head_mentor_for_request, status=RequestStatus.created)
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()

    update_data = {"extra_info": "Updated extra info"}
    response = await mentor_client.patch(f"/api/v1/request/{request.id}/self", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("extra_info") == "Updated extra info"


@pytest.mark.asyncio
async def test_update_request_self_as_mentor_other_mentor_request_forbidden(
    mentor_client: AsyncClient, request_for_other_mentor
):
    update_data = {"extra_info": "Should fail"}
    response = await mentor_client.patch(f"/api/v1/request/{request_for_other_mentor.id}/self", json=update_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_update_request_self_not_in_created_status(
    mentor_client: AsyncClient, async_session: AsyncSession, test_head_mentor_for_request
):
    result = await async_session.execute(select(MentorProfileORM).where(MentorProfileORM.email == "mentor@example.com"))
    mentor = result.scalar_one()

    request = RequestFactory(requester=mentor, receiver=test_head_mentor_for_request, status=RequestStatus.in_progress)
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()

    update_data = {"extra_info": "Should fail"}
    response = await mentor_client.patch(f"/api/v1/request/{request.id}/self", json=update_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "cannot be updated" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_update_request_self_not_found(mentor_client: AsyncClient):
    non_existent_id = uuid4()
    update_data = {"extra_info": "Updated"}
    response = await mentor_client.patch(f"/api/v1/request/{non_existent_id}/self", json=update_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "Request not found" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_update_request_self_unauthorized(unauthorized_client: AsyncClient):
    request_id = uuid4()
    update_data = {"extra_info": "Updated"}
    response = await unauthorized_client.patch(f"/api/v1/request/{request_id}/self", json=update_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED
