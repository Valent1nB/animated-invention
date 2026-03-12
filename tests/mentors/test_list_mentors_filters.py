import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK


@pytest.mark.asyncio
async def test_list_mentors_filter_by_search_email(
    superuser_client: AsyncClient, mentor_with_custom_email, jane_smith_mentor
):
    response = await superuser_client.get("/api/v1/mentor?search=john.doe")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["email"] == "john.doe@example.com" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_search_first_name(superuser_client: AsyncClient, alice_mentor, bob_mentor):
    response = await superuser_client.get("/api/v1/mentor?search=Alice")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["first_name"] == "Alice" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_search_last_name(
    superuser_client: AsyncClient, charlie_brown_mentor, david_wilson_mentor
):
    response = await superuser_client.get("/api/v1/mentor?search=Brown")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["last_name"] == "Brown" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_search_full_name(
    superuser_client: AsyncClient, emma_watson_mentor, frank_miller_mentor
):
    response = await superuser_client.get("/api/v1/mentor?search=Emma Watson")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["first_name"] == "Emma" and item["last_name"] == "Watson" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_search_city(superuser_client: AsyncClient, moscow_mentor, spb_mentor):
    response = await superuser_client.get("/api/v1/mentor?search=Moscow")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert any(item["city"] == "Moscow" for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_available_true(
    superuser_client: AsyncClient, available_mentor, unavailable_mentor
):
    response = await superuser_client.get("/api/v1/mentor?available=true")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["available"] is True for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_available_false(
    superuser_client: AsyncClient, available_mentor, unavailable_mentor
):
    response = await superuser_client.get("/api/v1/mentor?available=false")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["available"] is False for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_available_for_interview_true(
    superuser_client: AsyncClient, mentor_available_for_interview, mentor_not_available_for_interview
):
    response = await superuser_client.get("/api/v1/mentor?available_for_interview=true")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["available_for_interview"] is True for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_filter_by_available_for_interview_false(
    superuser_client: AsyncClient, mentor_available_for_interview, mentor_not_available_for_interview
):
    response = await superuser_client.get("/api/v1/mentor?available_for_interview=false")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["available_for_interview"] is False for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_order_by_full_name_asc(superuser_client: AsyncClient, zoe_zebra_mentor, alice_apple_mentor):
    response = await superuser_client.get("/api/v1/mentor?order_by=full_name&order_dir=asc")
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
async def test_list_mentors_order_by_full_name_desc(
    superuser_client: AsyncClient, alice_apple_mentor, zoe_zebra_mentor
):
    response = await superuser_client.get("/api/v1/mentor?order_by=full_name&order_dir=desc")
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
async def test_list_mentors_order_by_email_asc(superuser_client: AsyncClient, zebra_email_mentor, apple_email_mentor):
    response = await superuser_client.get("/api/v1/mentor?order_by=email&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    apple = next((item for item in items if item["email"] == "apple@example.com"), None)
    zebra = next((item for item in items if item["email"] == "zebra@example.com"), None)

    if apple and zebra:
        apple_idx = items.index(apple)
        zebra_idx = items.index(zebra)
        assert apple_idx < zebra_idx


@pytest.mark.asyncio
async def test_list_mentors_order_by_email_desc(superuser_client: AsyncClient, apple_email_mentor, zebra_email_mentor):
    response = await superuser_client.get("/api/v1/mentor?order_by=email&order_dir=desc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    apple = next((item for item in items if item["email"] == "apple@example.com"), None)
    zebra = next((item for item in items if item["email"] == "zebra@example.com"), None)

    if apple and zebra:
        apple_idx = items.index(apple)
        zebra_idx = items.index(zebra)
        assert zebra_idx < apple_idx


@pytest.mark.asyncio
async def test_list_mentors_order_by_city_asc(superuser_client: AsyncClient, zagreb_mentor, amsterdam_mentor):
    response = await superuser_client.get("/api/v1/mentor?order_by=city&order_dir=asc")
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
async def test_list_mentors_order_by_available_asc(superuser_client: AsyncClient, unavailable_mentor, available_mentor):
    response = await superuser_client.get("/api/v1/mentor?order_by=available&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    false_mentors = [item for item in items if item["available"] is False]
    true_mentors = [item for item in items if item["available"] is True]

    if false_mentors and true_mentors:
        first_false_idx = items.index(false_mentors[0])
        first_true_idx = items.index(true_mentors[0])
        assert first_false_idx < first_true_idx


@pytest.mark.asyncio
async def test_list_mentors_order_by_available_for_interview_asc(
    superuser_client: AsyncClient, mentor_not_available_for_interview, mentor_available_for_interview
):
    response = await superuser_client.get("/api/v1/mentor?order_by=available_for_interview&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    false_mentors = [item for item in items if item["available_for_interview"] is False]
    true_mentors = [item for item in items if item["available_for_interview"] is True]

    if false_mentors and true_mentors:
        first_false_idx = items.index(false_mentors[0])
        first_true_idx = items.index(true_mentors[0])
        assert first_false_idx < first_true_idx


@pytest.mark.asyncio
async def test_list_mentors_pagination_limit(superuser_client: AsyncClient, multiple_mentors):
    response = await superuser_client.get("/api/v1/mentor?limit=3")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["limit"] == 3
    assert len(json_data["items"]) == 3
    assert json_data["total"] >= 5


@pytest.mark.asyncio
async def test_list_mentors_combination_search_and_available(
    superuser_client: AsyncClient, john_doe_mentor, john_smith_mentor, jane_doe_mentor
):
    response = await superuser_client.get("/api/v1/mentor?search=John&available=true")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["available"] is True for item in json_data["items"])
    assert all("John" in item["first_name"] for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_combination_available_and_available_for_interview(
    superuser_client: AsyncClient,
    mentor_available_and_interview,
    mentor_available_not_interview,
    mentor_unavailable_and_interview,
):
    response = await superuser_client.get("/api/v1/mentor?available=true&available_for_interview=true")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] >= 1
    assert all(item["available"] is True for item in json_data["items"])
    assert all(item["available_for_interview"] is True for item in json_data["items"])


@pytest.mark.asyncio
async def test_list_mentors_combination_search_and_order(
    superuser_client: AsyncClient, zoe_zebra_zagreb_mentor, alice_apple_amsterdam_mentor
):
    response = await superuser_client.get("/api/v1/mentor?search=Z&order_by=city&order_dir=asc")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    items = json_data["items"]
    cities = [item["city"] for item in items if "Z" in item["first_name"] or "Z" in item["city"]]
    assert cities == sorted(cities)


@pytest.mark.asyncio
async def test_list_mentors_combination_all_filters(
    superuser_client: AsyncClient, john_doe_moscow_mentor, john_smith_spb_mentor, jane_doe_moscow_mentor
):
    response = await superuser_client.get(
        "/api/v1/mentor?search=John&available=true&available_for_interview=true"
        "&order_by=email&order_dir=asc&limit=10&offset=0"
    )
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data["limit"] == 10
    assert json_data["offset"] == 0
    assert json_data["total"] >= 1
    assert all(item["available"] is True for item in json_data["items"])
    assert all(item["available_for_interview"] is True for item in json_data["items"])
    assert all("John" in item["first_name"] for item in json_data["items"])
    emails = [item["email"] for item in json_data["items"]]
    assert emails == sorted(emails)
