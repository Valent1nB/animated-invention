from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)


@pytest.mark.asyncio
async def test_reassign_mentor_as_superuser(superuser_client: AsyncClient, test_intern, other_mentor_for_intern):
    reassign_data = {"new_mentor_id": str(other_mentor_for_intern.id)}
    response = await superuser_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("mentor", {}).get("id") == str(other_mentor_for_intern.id)


@pytest.mark.asyncio
async def test_reassign_mentor_as_head_mentor(head_mentor_client: AsyncClient, test_intern, other_mentor_for_intern):
    reassign_data = {"new_mentor_id": str(other_mentor_for_intern.id)}
    response = await head_mentor_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("mentor", {}).get("id") == str(other_mentor_for_intern.id)


@pytest.mark.asyncio
async def test_reassign_mentor_as_mentor_forbidden(mentor_client: AsyncClient, test_intern, other_mentor_for_intern):
    reassign_data = {"new_mentor_id": str(other_mentor_for_intern.id)}
    response = await mentor_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_reassign_mentor_to_archived_mentor(
    superuser_client: AsyncClient, test_intern, archived_mentor_for_intern
):
    reassign_data = {"new_mentor_id": str(archived_mentor_for_intern.id)}
    response = await superuser_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == "Mentor is archived"


@pytest.mark.asyncio
async def test_reassign_mentor_not_found(superuser_client: AsyncClient, other_mentor_for_intern):
    non_existent_id = uuid4()
    reassign_data = {"new_mentor_id": str(other_mentor_for_intern.id)}
    response = await superuser_client.patch(
        f"/api/v1/intern/{non_existent_id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Intern not found"


@pytest.mark.asyncio
async def test_reassign_mentor_invalid_mentor(superuser_client: AsyncClient, test_intern):
    invalid_mentor_id = uuid4()
    reassign_data = {"new_mentor_id": str(invalid_mentor_id)}
    response = await superuser_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == "Mentor not found"


@pytest.mark.asyncio
async def test_reassign_mentor_head_mentor_to_other_unit_forbidden(
    head_mentor_client: AsyncClient, test_intern, mentor_other_unit
):
    """Head mentor cannot reassign intern to a mentor from another unit."""
    reassign_data = {"new_mentor_id": str(mentor_other_unit.id)}
    response = await head_mentor_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert "unit" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_reassign_mentor_unauthorized(unauthorized_client: AsyncClient, test_intern, other_mentor_for_intern):
    reassign_data = {"new_mentor_id": str(other_mentor_for_intern.id)}
    response = await unauthorized_client.patch(
        f"/api/v1/intern/{test_intern.id}/reassign-mentor",
        json=reassign_data,
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED
