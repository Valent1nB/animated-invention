from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.domain.entities.employee.enum import RequestTopic


@pytest.mark.asyncio
async def test_create_request_as_superuser(superuser_client: AsyncClient, test_head_mentor_for_request):
    request_data = {
        "receiver_id": str(test_head_mentor_for_request.id),
        "topic": RequestTopic.give_cv,
        "extra_info": "Need CV for intern",
    }
    response = await superuser_client.post("/api/v1/request", json=request_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("topic") == RequestTopic.give_cv
    assert json_data.get("extra_info") == "Need CV for intern"
    assert json_data.get("status") == "created"
    assert json_data.get("receiver", {}).get("id") == str(test_head_mentor_for_request.id)


@pytest.mark.asyncio
async def test_create_request_as_head_mentor(head_mentor_client: AsyncClient, test_head_mentor_for_request):
    request_data = {
        "receiver_id": str(test_head_mentor_for_request.id),
        "topic": RequestTopic.add_to_checks,
        "extra_info": "Add intern to checks",
    }
    response = await head_mentor_client.post("/api/v1/request", json=request_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("topic") == RequestTopic.add_to_checks


@pytest.mark.asyncio
async def test_create_request_as_mentor(mentor_client: AsyncClient, test_head_mentor_for_request):
    request_data = {
        "receiver_id": str(test_head_mentor_for_request.id),
        "topic": RequestTopic.create_aws_acc,
        "extra_info": "Create AWS account",
    }
    response = await mentor_client.post("/api/v1/request", json=request_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("topic") == RequestTopic.create_aws_acc


@pytest.mark.asyncio
async def test_create_request_with_non_head_mentor_receiver(mentor_client: AsyncClient, test_mentor_for_request):
    request_data = {
        "receiver_id": str(test_mentor_for_request.id),
        "topic": RequestTopic.other,
    }
    response = await mentor_client.post("/api/v1/request", json=request_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert "mentor can only create requests to head mentors" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_request_with_invalid_receiver(mentor_client: AsyncClient):
    request_data = {
        "receiver_id": str(uuid4()),
        "topic": RequestTopic.other,
    }
    response = await mentor_client.post("/api/v1/request", json=request_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert "not found" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_request_unauthorized(unauthorized_client: AsyncClient, test_head_mentor_for_request):
    request_data = {
        "receiver_id": str(test_head_mentor_for_request.id),
        "topic": RequestTopic.other,
    }
    response = await unauthorized_client.post("/api/v1/request", json=request_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED
