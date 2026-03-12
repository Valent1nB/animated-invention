from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.domain.entities.employee.enum import RequestStatus


@pytest.mark.asyncio
async def test_update_request_as_superuser(superuser_client: AsyncClient, test_request_created):
    update_data = {
        "status": RequestStatus.in_progress,
        "comment_from_receiver": "Working on it",
    }
    response = await superuser_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("status") == RequestStatus.in_progress
    assert json_data.get("comment_from_receiver") == "Working on it"


@pytest.mark.asyncio
async def test_update_request_as_head_mentor(head_mentor_client: AsyncClient, test_request_created):
    update_data = {
        "status": RequestStatus.completed,
        "comment_from_receiver": "Done!",
    }
    response = await head_mentor_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("status") == RequestStatus.completed
    assert json_data.get("comment_from_receiver") == "Done!"
    assert json_data.get("closed_at") is not None


@pytest.mark.asyncio
async def test_update_request_as_mentor_forbidden(mentor_client: AsyncClient, test_request_created):
    update_data = {"status": RequestStatus.in_progress}
    response = await mentor_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_update_request_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    update_data = {"status": RequestStatus.in_progress}
    response = await superuser_client.patch(f"/api/v1/request/{non_existent_id}", json=update_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Request not found"


@pytest.mark.asyncio
async def test_update_request_unauthorized(unauthorized_client: AsyncClient):
    request_id = uuid4()
    update_data = {"status": RequestStatus.in_progress}
    response = await unauthorized_client.patch(f"/api/v1/request/{request_id}", json=update_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_request_only_status(superuser_client: AsyncClient, test_request_created):
    update_data = {"status": RequestStatus.in_progress}
    response = await superuser_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("status") == RequestStatus.in_progress


@pytest.mark.asyncio
async def test_update_request_only_comment(superuser_client: AsyncClient, test_request_created):
    update_data = {"comment_from_receiver": "New comment"}
    response = await superuser_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("comment_from_receiver") == "New comment"


@pytest.mark.asyncio
async def test_update_request_to_canceled_sets_closed_at(superuser_client: AsyncClient, test_request_created):
    update_data = {"status": RequestStatus.canceled}
    response = await superuser_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("status") == RequestStatus.canceled
    assert json_data.get("closed_at") is not None


@pytest.mark.asyncio
async def test_update_request_to_completed_sets_closed_at(superuser_client: AsyncClient, test_request_created):
    update_data = {"status": RequestStatus.completed}
    response = await superuser_client.patch(f"/api/v1/request/{test_request_created.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("status") == RequestStatus.completed
    assert json_data.get("closed_at") is not None
