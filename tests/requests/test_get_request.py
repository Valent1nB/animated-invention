from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.domain.entities.employee.enum import Role
from app.infrastructure.database import MentorProfile as MentorProfileORM
from tests.factories.mentor import MentorFactory
from tests.factories.request import RequestFactory


@pytest.mark.asyncio
async def test_get_request_as_superuser(superuser_client: AsyncClient, test_request):
    response = await superuser_client.get(f"/api/v1/request/{test_request.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(test_request.id)
    assert json_data.get("topic") == test_request.topic


@pytest.mark.asyncio
async def test_get_request_as_head_mentor(head_mentor_client: AsyncClient, test_request):
    response = await head_mentor_client.get(f"/api/v1/request/{test_request.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(test_request.id)


@pytest.mark.asyncio
async def test_get_request_as_mentor_own_request(mentor_client: AsyncClient, async_session: AsyncSession):
    result = await async_session.execute(select(MentorProfileORM).where(MentorProfileORM.email == "mentor@example.com"))
    mentor = result.scalar_one()

    head_mentor = MentorFactory(role=Role.head_mentor)
    if head_mentor not in async_session:
        async_session.add(head_mentor)
    await async_session.flush()

    request = RequestFactory(requester=mentor, receiver=head_mentor)
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()

    response = await mentor_client.get(f"/api/v1/request/{request.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(request.id)


@pytest.mark.asyncio
async def test_get_request_as_mentor_other_mentor_request(mentor_client: AsyncClient, request_for_other_mentor):
    response = await mentor_client.get(f"/api/v1/request/{request_for_other_mentor.id}")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_get_request_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    response = await superuser_client.get(f"/api/v1/request/{non_existent_id}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Request not found"


@pytest.mark.asyncio
async def test_get_request_unauthorized(unauthorized_client: AsyncClient):
    request_id = uuid4()
    response = await unauthorized_client.get(f"/api/v1/request/{request_id}")
    assert response.status_code == HTTP_401_UNAUTHORIZED
