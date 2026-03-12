import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

from app.infrastructure.database.models.employee import MentorProfile


@pytest.mark.asyncio
async def test_intern_stats_historical_basic(
    superuser_client: AsyncClient,
    sold_in_jan_intern,
    laid_off_in_jan_intern,
    sold_in_feb_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 2
    assert data["by_status"]["sold"] == 1
    assert data["by_status"]["laid_off"] == 1


@pytest.mark.asyncio
async def test_intern_stats_historical_filter_by_mentor(
    superuser_client: AsyncClient,
    stats_mentor1,
    sold_m1_intern,
    sold_m2_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "mentor_id": str(stats_mentor1.id),
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 1
    assert data["by_status"]["sold"] == 1


@pytest.mark.asyncio
async def test_intern_stats_comparison_two_periods(
    superuser_client: AsyncClient,
    prev_period_sold_intern,
    curr_period_sold_intern1,
    curr_period_sold_intern2,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["current"]["total"] == 2
    assert data["previous"]["total"] == 1
    assert data["absolute_change"] == 1
    assert pytest.approx(data["percent_change"], rel=1e-3) == 100.0


@pytest.mark.asyncio
async def test_intern_snapshot_filters_by_status_english_city_and_ready_for_sale(
    superuser_client: AsyncClient,
    snapshot_match_intern,
    snapshot_wrong_english_intern,
    snapshot_wrong_city_intern,
    snapshot_wrong_status_intern,
    snapshot_wrong_ready_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/current",
        params={
            "statuses": "active",
            "english_levels": "B1",
            "cities": "Moscow",
            "ready_for_sale": "true",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 1
    assert data["by_status"]["active"] == 1


@pytest.mark.asyncio
async def test_intern_snapshot_mentor_sees_only_own(
    mentor_client: AsyncClient,
    mentor: MentorProfile,
    intern_for_logged_in_mentor,
    intern_for_other_mentor,
):
    response = await mentor_client.get("/api/v1/intern/stats/current")
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 1


@pytest.mark.asyncio
async def test_intern_stats_historical_mentor_cannot_request_other_mentor(
    mentor_client: AsyncClient,
    mentor: MentorProfile,
    other_mentor_for_stats,
):
    response = await mentor_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "mentor_id": str(other_mentor_for_stats.id),
        },
    )
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_intern_snapshot_mentor_cannot_request_other_mentor(
    mentor_client: AsyncClient,
    mentor: MentorProfile,
    other_mentor2_for_stats,
):
    response = await mentor_client.get(
        "/api/v1/intern/stats/current",
        params={"mentor_id": str(other_mentor2_for_stats.id)},
    )
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_intern_stats_historical_as_head_mentor(
    head_mentor_client: AsyncClient,
    sold_in_jan_intern,
    laid_off_in_jan_intern,
    sold_in_feb_intern,
):
    response = await head_mentor_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 2
    assert data["by_status"]["sold"] == 1
    assert data["by_status"]["laid_off"] == 1


@pytest.mark.asyncio
async def test_intern_stats_historical_filter_by_statuses(
    superuser_client: AsyncClient,
    sold_in_jan_intern,
    laid_off_in_jan_intern,
    sold_in_feb_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "statuses": ["sold"],
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 1
    assert data["by_status"]["sold"] == 1
    assert data["by_status"].get("laid_off", 0) == 0


@pytest.mark.asyncio
async def test_intern_stats_historical_empty_period(
    superuser_client: AsyncClient,
    sold_in_jan_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2027-01-01",
            "end_date": "2027-01-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 0


@pytest.mark.asyncio
async def test_intern_stats_historical_unauthorized(unauthorized_client: AsyncClient):
    response = await unauthorized_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_intern_stats_historical_head_mentor_filter_by_mentor(
    head_mentor_client: AsyncClient,
    stats_mentor1,
    sold_m1_intern,
    sold_m2_intern,
):
    response = await head_mentor_client.get(
        "/api/v1/intern/stats",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "mentor_id": str(stats_mentor1.id),
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] == 1
    assert data["by_status"]["sold"] == 1


@pytest.mark.asyncio
async def test_intern_snapshot_stats_as_head_mentor(
    head_mentor_client: AsyncClient,
    snapshot_match_intern,
    snapshot_wrong_english_intern,
):
    response = await head_mentor_client.get("/api/v1/intern/stats/current")
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_intern_snapshot_stats_filter_by_statuses(
    superuser_client: AsyncClient,
    snapshot_match_intern,
    snapshot_wrong_status_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/current",
        params={
            "statuses": ["active"],
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["by_status"]["active"] >= 1


@pytest.mark.asyncio
async def test_intern_snapshot_stats_filter_by_english_levels(
    superuser_client: AsyncClient,
    snapshot_match_intern,
    snapshot_wrong_english_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/current",
        params={
            "english_levels": ["B1"],
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_intern_snapshot_stats_filter_by_cities(
    superuser_client: AsyncClient,
    snapshot_match_intern,
    snapshot_wrong_city_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/current",
        params={
            "cities": ["Moscow"],
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_intern_snapshot_stats_filter_by_ready_for_sale_false(
    superuser_client: AsyncClient,
    snapshot_match_intern,
    snapshot_wrong_ready_intern,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/current",
        params={
            "ready_for_sale": "false",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_intern_snapshot_stats_empty_filters(
    superuser_client: AsyncClient,
):
    response = await superuser_client.get("/api/v1/intern/stats/current")
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert "total" in data
    assert "by_status" in data


@pytest.mark.asyncio
async def test_intern_snapshot_stats_unauthorized(unauthorized_client: AsyncClient):
    response = await unauthorized_client.get("/api/v1/intern/stats/current")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_intern_snapshot_stats_head_mentor_filter_by_mentor(
    head_mentor_client: AsyncClient,
    snapshot_mentor,
    snapshot_match_intern,
):
    response = await head_mentor_client.get(
        "/api/v1/intern/stats/current",
        params={"mentor_id": str(snapshot_mentor.id)},
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_intern_stats_comparison_as_head_mentor(
    head_mentor_client: AsyncClient,
    prev_period_sold_intern,
    curr_period_sold_intern1,
    curr_period_sold_intern2,
):
    response = await head_mentor_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["current"]["total"] == 2
    assert data["previous"]["total"] == 1
    assert data["absolute_change"] == 1


@pytest.mark.asyncio
async def test_intern_stats_comparison_negative_change(
    superuser_client: AsyncClient,
    prev_period_sold_intern,
    curr_period_sold_intern1,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["current"]["total"] == 1
    assert data["previous"]["total"] == 1
    assert data["absolute_change"] == 0


@pytest.mark.asyncio
async def test_intern_stats_comparison_empty_periods(
    superuser_client: AsyncClient,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2027-01-01",
            "current_end_date": "2027-01-31",
            "previous_start_date": "2026-12-01",
            "previous_end_date": "2026-12-31",
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert data["current"]["total"] == 0
    assert data["previous"]["total"] == 0
    assert data["absolute_change"] == 0


@pytest.mark.asyncio
async def test_intern_stats_comparison_filter_by_mentor(
    superuser_client: AsyncClient,
    stats_mentor,
    prev_period_sold_intern,
    curr_period_sold_intern1,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
            "mentor_id": str(stats_mentor.id),
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert "current" in data
    assert "previous" in data
    assert "absolute_change" in data
    assert "percent_change" in data


@pytest.mark.asyncio
async def test_intern_stats_comparison_filter_by_statuses(
    superuser_client: AsyncClient,
    prev_period_sold_intern,
    curr_period_sold_intern1,
    curr_period_sold_intern2,
):
    response = await superuser_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
            "statuses": ["sold"],
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()

    assert "current" in data
    assert "previous" in data


@pytest.mark.asyncio
async def test_intern_stats_comparison_unauthorized(unauthorized_client: AsyncClient):
    response = await unauthorized_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
        },
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_intern_stats_comparison_mentor_cannot_request_other_mentor(
    mentor_client: AsyncClient,
    mentor: MentorProfile,
    other_mentor_for_stats,
):
    response = await mentor_client.get(
        "/api/v1/intern/stats/comparison",
        params={
            "current_start_date": "2026-01-01",
            "current_end_date": "2026-01-31",
            "previous_start_date": "2025-12-01",
            "previous_end_date": "2025-12-31",
            "mentor_id": str(other_mentor_for_stats.id),
        },
    )
    assert response.status_code == HTTP_403_FORBIDDEN
