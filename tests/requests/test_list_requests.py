import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK

from app.domain.entities.employee.enum import RequestStatus, RequestTopic


@pytest.mark.asyncio
async def test_list_requests_as_superuser(superuser_client: AsyncClient, multiple_requests):
    response = await superuser_client.get("/api/v1/request")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 5
    assert len(json_data["items"]) >= 5


@pytest.mark.asyncio
async def test_list_requests_as_head_mentor(head_mentor_client: AsyncClient, test_request):
    response = await head_mentor_client.get("/api/v1/request")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    # Head mentor should see requests where he is receiver
    assert any(item["receiver"]["id"] == str(test_request.receiver_id) for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_as_mentor(mentor_client: AsyncClient, test_request_created, test_mentor_for_request):
    response = await mentor_client.get("/api/v1/request")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    # Mentor should see only their own requests
    assert all(item["requester"]["id"] == str(test_mentor_for_request.id) for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_filter_by_status_created(
    superuser_client: AsyncClient, test_request_created, test_request_in_progress
):
    response = await superuser_client.get("/api/v1/request?status=created")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["status"] == RequestStatus.created for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_filter_by_status_in_progress(
    superuser_client: AsyncClient, test_request_created, test_request_in_progress
):
    response = await superuser_client.get("/api/v1/request?status=in_progress")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["status"] == RequestStatus.in_progress for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_filter_by_topic_give_cv(
    superuser_client: AsyncClient, test_request_give_cv, test_request_add_to_checks
):
    response = await superuser_client.get("/api/v1/request?topic=give_cv")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["topic"] == RequestTopic.give_cv for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_filter_by_topic_add_to_checks(
    superuser_client: AsyncClient, test_request_give_cv, test_request_add_to_checks
):
    response = await superuser_client.get("/api/v1/request?topic=add_to_checks")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["topic"] == RequestTopic.add_to_checks for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_filter_by_requester_id(
    superuser_client: AsyncClient, test_request_created, request_for_other_mentor
):
    requester_id = test_request_created.requester_id
    response = await superuser_client.get(f"/api/v1/request?requester_id={requester_id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["requester"]["id"] == str(requester_id) for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_filter_by_receiver_id(
    superuser_client: AsyncClient, test_request_created, test_head_mentor_for_request
):
    receiver_id = test_head_mentor_for_request.id
    response = await superuser_client.get(f"/api/v1/request?receiver_id={receiver_id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["receiver"]["id"] == str(receiver_id) for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_order_by_created_at_desc(superuser_client: AsyncClient, multiple_requests):
    response = await superuser_client.get("/api/v1/request?order_by=created_at&order_dir=desc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    if len(items) > 1:
        # Check that items are sorted by created_at descending
        for i in range(len(items) - 1):
            assert items[i]["created_at"] >= items[i + 1]["created_at"]


@pytest.mark.asyncio
async def test_list_requests_pagination_limit(superuser_client: AsyncClient, multiple_requests):
    response = await superuser_client.get("/api/v1/request?limit=3")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["limit"] == 3
    assert len(json_data["items"]) == 3
    assert json_data["total"] >= 5


@pytest.mark.asyncio
async def test_list_requests_combination_filters(
    superuser_client: AsyncClient,
    test_request_created,
    test_request_in_progress,
    test_request_give_cv,
):
    response = await superuser_client.get("/api/v1/request?status=created&topic=give_cv")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert all(item["status"] == RequestStatus.created for item in json_data["items"])
    assert all(item["topic"] == RequestTopic.give_cv for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_requests_mentor_cannot_see_other_mentor_requests(
    mentor_client: AsyncClient, request_for_other_mentor, test_mentor_for_request
):
    response = await mentor_client.get("/api/v1/request")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    # Mentor should not see other mentor's requests
    assert all(item["requester"]["id"] == str(test_mentor_for_request.id) for item in json_data["items"])
