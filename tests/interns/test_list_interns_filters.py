import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from app.infrastructure.database.models.employee import MentorProfile


@pytest.mark.asyncio
async def test_list_interns_filter_by_search_email(
    superuser_client: AsyncClient,
    intern_with_custom_email,
    other_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=intern.doe")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["email"] == "intern.doe@example.com" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_search_first_name(
    superuser_client: AsyncClient,
    alice_intern,
    bob_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=Alice")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["first_name"] == "Alice" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_search_last_name(
    superuser_client: AsyncClient,
    charlie_brown_intern,
    david_wilson_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=Brown")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["last_name"] == "Brown" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_search_full_name(
    superuser_client: AsyncClient,
    emma_watson_intern,
    frank_miller_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=Emma Watson")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["first_name"] == "Emma" and item["last_name"] == "Watson" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_search_city(
    superuser_client: AsyncClient,
    moscow_intern,
    spb_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=Moscow")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["city"] == "Moscow" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_status(
    superuser_client: AsyncClient,
    active_intern,
    awaited_intern,
):
    response = await superuser_client.get("/api/v1/intern?status=active")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["status"] == "active" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_employment_status(
    superuser_client: AsyncClient,
    employed_intern,
    student_intern,
):
    response = await superuser_client.get("/api/v1/intern?employment_status=employed")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["employment_status"] == "employed" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_english_level(
    superuser_client: AsyncClient,
    b1_intern,
    c1_intern,
):
    response = await superuser_client.get("/api/v1/intern?english_level=B1")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["english_level"] == "B1" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_filter_by_mentor_id(
    superuser_client: AsyncClient,
    mentor_with_interns,
    another_mentor_with_interns,
):
    mentor, interns = mentor_with_interns
    response = await superuser_client.get(f"/api/v1/intern?mentor_id={mentor.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == len(interns)
    mentor_ids = {item["mentor"]["id"] for item in json_data["items"]}
    assert mentor_ids == {str(mentor.id)}


@pytest.mark.asyncio
async def test_list_interns_order_by_full_name_asc(
    superuser_client: AsyncClient,
    zoe_zebra_intern,
    alice_apple_intern,
):
    response = await superuser_client.get("/api/v1/intern?order_by=full_name&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    alice = next((item for item in items if item["first_name"] == "Alice"), None)
    zoe = next((item for item in items if item["first_name"] == "Zoe"), None)

    if alice and zoe:
        alice_idx = items.index(alice)
        zoe_idx = items.index(zoe)
        assert alice_idx < zoe_idx


@pytest.mark.asyncio
async def test_list_interns_order_by_full_name_desc(
    superuser_client: AsyncClient,
    alice_apple_intern,
    zoe_zebra_intern,
):
    response = await superuser_client.get("/api/v1/intern?order_by=full_name&order_dir=desc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    alice = next((item for item in items if item["first_name"] == "Alice"), None)
    zoe = next((item for item in items if item["first_name"] == "Zoe"), None)

    if alice and zoe:
        alice_idx = items.index(alice)
        zoe_idx = items.index(zoe)
        assert zoe_idx < alice_idx


@pytest.mark.asyncio
async def test_list_interns_order_by_email_asc(
    superuser_client: AsyncClient,
    zebra_email_intern,
    apple_email_intern,
):
    response = await superuser_client.get("/api/v1/intern?order_by=email&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    apple = next((item for item in items if item["email"] == "apple.intern@example.com"), None)
    zebra = next((item for item in items if item["email"] == "zebra.intern@example.com"), None)

    if apple and zebra:
        apple_idx = items.index(apple)
        zebra_idx = items.index(zebra)
        assert apple_idx < zebra_idx


@pytest.mark.asyncio
async def test_list_interns_order_by_email_desc(
    superuser_client: AsyncClient,
    apple_email_intern,
    zebra_email_intern,
):
    response = await superuser_client.get("/api/v1/intern?order_by=email&order_dir=desc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    apple = next((item for item in items if item["email"] == "apple.intern@example.com"), None)
    zebra = next((item for item in items if item["email"] == "zebra.intern@example.com"), None)

    if apple and zebra:
        apple_idx = items.index(apple)
        zebra_idx = items.index(zebra)
        assert zebra_idx < apple_idx


@pytest.mark.asyncio
async def test_list_interns_order_by_city_asc(
    superuser_client: AsyncClient,
    zagreb_intern,
    amsterdam_intern,
):
    response = await superuser_client.get("/api/v1/intern?order_by=city&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    amsterdam = next((item for item in items if item["city"] == "Amsterdam"), None)
    zagreb = next((item for item in items if item["city"] == "Zagreb"), None)

    if amsterdam and zagreb:
        amsterdam_idx = items.index(amsterdam)
        zagreb_idx = items.index(zagreb)
        assert amsterdam_idx < zagreb_idx


@pytest.mark.asyncio
async def test_list_interns_pagination_limit(
    superuser_client: AsyncClient,
    multiple_interns,
):
    response = await superuser_client.get("/api/v1/intern?limit=3")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["limit"] == 3
    assert len(json_data["items"]) == 3
    assert json_data["total"] >= len(multiple_interns)


@pytest.mark.asyncio
async def test_list_interns_combination_search_and_status(
    superuser_client: AsyncClient,
    active_intern,
    awaited_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=intern&status=active")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["status"] == "active" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_combination_search_and_order(
    superuser_client: AsyncClient,
    zoe_zebra_intern,
    alice_apple_intern,
):
    response = await superuser_client.get("/api/v1/intern?search=Z&order_by=city&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    cities = [item["city"] for item in items if "Z" in item["first_name"] or "Z" in item["city"]]
    assert cities == sorted(cities)


# Role-based access tests


@pytest.mark.asyncio
async def test_list_interns_superuser_sees_all(
    superuser_client: AsyncClient,
    mentor_with_interns,
    another_mentor_with_interns,
):
    response = await superuser_client.get("/api/v1/intern")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    total_ids = {item["id"] for item in json_data["items"]}
    _, interns1 = mentor_with_interns
    _, interns2 = another_mentor_with_interns
    expected_ids = {str(i.id) for i in interns1 + interns2}
    assert expected_ids.issubset(total_ids)


@pytest.mark.asyncio
async def test_list_interns_head_mentor_sees_all(
    head_mentor_client: AsyncClient,
    mentor_with_interns,
    another_mentor_with_interns,
):
    response = await head_mentor_client.get("/api/v1/intern")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    total_ids = {item["id"] for item in json_data["items"]}
    _, interns1 = mentor_with_interns
    _, interns2 = another_mentor_with_interns
    expected_ids = {str(i.id) for i in interns1 + interns2}
    assert expected_ids.issubset(total_ids)


@pytest.mark.asyncio
async def test_list_interns_mentor_sees_only_own(
    mentor_client: AsyncClient,
    mentor: MentorProfile,
    intern_for_logged_in_mentor,
    intern_for_other_mentor,
):
    response = await mentor_client.get("/api/v1/intern")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["mentor"]["id"] == str(mentor.id) for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_mentor_cannot_filter_other_mentor(
    mentor_client: AsyncClient,
    intern_for_other_mentor,
):
    other_mentor_id = intern_for_other_mentor.mentor_id

    response = await mentor_client.get(f"/api/v1/intern?mentor_id={other_mentor_id}")
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_list_interns_mentor_can_filter_own_interns(
    mentor_client: AsyncClient,
    mentor: MentorProfile,
    intern_for_logged_in_mentor,
    intern_for_other_mentor,
):
    response = await mentor_client.get(f"/api/v1/intern?mentor_id={mentor.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["mentor"]["id"] == str(mentor.id) for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_interns_head_mentor_filter_other_unit_forbidden(head_mentor_client: AsyncClient, another_unit):
    """Head mentor cannot filter interns by unit_id other than their own."""
    response = await head_mentor_client.get(f"/api/v1/intern?unit_id={another_unit.id}")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Head mentor can only filter by their own unit"
