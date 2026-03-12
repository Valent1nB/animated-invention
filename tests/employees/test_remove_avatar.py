from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_avatar_for_mentor_as_superuser(superuser_client: AsyncClient, mentor_with_avatar):
    response = await superuser_client.delete(f"/api/v1/employee/{mentor_with_avatar.id}/remove-avatar")
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_avatar_for_mentor_as_head_mentor(head_mentor_client: AsyncClient, mentor_with_avatar):
    response = await head_mentor_client.delete(f"/api/v1/employee/{mentor_with_avatar.id}/remove-avatar")
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_avatar_for_self_as_mentor(mentor, mentor_client: AsyncClient, async_session):
    # Set avatar for mentor
    mentor.avatar_key = "avatars/test_avatar.png"
    await async_session.flush()

    response = await mentor_client.delete(f"/api/v1/employee/{mentor.id}/remove-avatar")
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_avatar_for_intern_as_superuser(superuser_client: AsyncClient, intern_with_avatar):
    response = await superuser_client.delete(f"/api/v1/employee/{intern_with_avatar.id}/remove-avatar")
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_avatar_for_own_intern_as_mentor(
    mentor, mentor_client: AsyncClient, intern_for_logged_in_mentor, async_session
):
    # Set avatar for intern
    intern_for_logged_in_mentor.avatar_key = "avatars/test_intern_avatar.png"
    await async_session.flush()

    response = await mentor_client.delete(f"/api/v1/employee/{intern_for_logged_in_mentor.id}/remove-avatar")
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_avatar_for_other_mentor_as_mentor_forbidden(mentor_client: AsyncClient, other_mentor_for_avatar):
    response = await mentor_client.delete(f"/api/v1/employee/{other_mentor_for_avatar.id}/remove-avatar")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_remove_avatar_for_other_intern_as_mentor_forbidden(mentor_client: AsyncClient, intern_with_other_mentor):
    response = await mentor_client.delete(f"/api/v1/employee/{intern_with_other_mentor.id}/remove-avatar")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_remove_avatar_employee_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    response = await superuser_client.delete(f"/api/v1/employee/{non_existent_id}/remove-avatar")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Employee not found"


@pytest.mark.asyncio
async def test_remove_avatar_unauthorized(unauthorized_client: AsyncClient):
    employee_id = uuid4()
    response = await unauthorized_client.delete(f"/api/v1/employee/{employee_id}/remove-avatar")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_remove_avatar_when_no_avatar_exists(
    superuser_client: AsyncClient, test_mentor_for_avatar, async_session
):
    test_mentor_for_avatar.avatar_key = ""
    await async_session.flush()

    response = await superuser_client.delete(f"/api/v1/employee/{test_mentor_for_avatar.id}/remove-avatar")
    assert response.status_code == HTTP_204_NO_CONTENT
