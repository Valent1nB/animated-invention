from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.employee.enum import EmploymentStatus, EnglishLevel, InternshipStatus
from tests.factories.intern import InternFactory
from tests.factories.mentor import MentorFactory


@pytest.fixture
async def test_mentor_for_intern(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def test_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(mentor=test_mentor_for_intern)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def other_mentor_for_intern(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def other_intern(async_session: AsyncSession, other_mentor_for_intern):
    intern = InternFactory(mentor=other_mentor_for_intern)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def archived_mentor_for_intern(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(available=False, available_for_interview=False, unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def mentor_other_unit(async_session: AsyncSession, another_unit):
    """Mentor in a different unit (for head_mentor cross-unit forbidden tests)."""
    mentor = MentorFactory(unit=another_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def multiple_interns(async_session: AsyncSession, test_mentor_for_intern):
    interns = [InternFactory(mentor=test_mentor_for_intern) for _ in range(5)]
    for intern in interns:
        if intern not in async_session:
            async_session.add(intern)
    await async_session.flush()
    return interns


# Search fixtures


@pytest.fixture
async def intern_with_custom_email(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        email="intern.doe@example.com",
        first_name="John",
        last_name="Doe",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def jane_smith_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        email="jane.smith.intern@example.com",
        first_name="Jane",
        last_name="Smith",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def alice_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Alice",
        last_name="Wonder",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def bob_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Bob",
        last_name="Builder",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def charlie_brown_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Charlie",
        last_name="Brown",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def david_wilson_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="David",
        last_name="Wilson",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def emma_watson_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Emma",
        last_name="Watson",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def frank_miller_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Frank",
        last_name="Miller",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def moscow_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        city="Moscow",
        first_name="Ivan",
        last_name="Ivanov",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def spb_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        city="Saint Petersburg",
        first_name="Petr",
        last_name="Petrov",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def zoe_zebra_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Zoe",
        last_name="Zebra",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def alice_apple_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        first_name="Alice",
        last_name="Apple",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def zebra_email_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        email="zebra.intern@example.com",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def apple_email_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        email="apple.intern@example.com",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def zagreb_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        city="Zagreb",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def amsterdam_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        city="Amsterdam",
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


# Filter-specific fixtures


@pytest.fixture
async def active_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        status=InternshipStatus.active,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def awaited_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        status=InternshipStatus.awaited,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def employed_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        employment_status=EmploymentStatus.employed,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def student_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        employment_status=EmploymentStatus.student,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def b1_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        english_level=EnglishLevel.B1,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def c1_intern(async_session: AsyncSession, test_mentor_for_intern):
    intern = InternFactory(
        mentor=test_mentor_for_intern,
        english_level=EnglishLevel.C1,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


# Role / constraints fixtures


@pytest.fixture
async def mentor_with_interns(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    interns = [InternFactory(mentor=mentor) for _ in range(3)]
    if mentor not in async_session:
        async_session.add(mentor)
    for intern in interns:
        if intern not in async_session:
            async_session.add(intern)
    await async_session.flush()
    return mentor, interns


@pytest.fixture
async def another_mentor_with_interns(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    interns = [InternFactory(mentor=mentor) for _ in range(2)]
    if mentor not in async_session:
        async_session.add(mentor)
    for intern in interns:
        if intern not in async_session:
            async_session.add(intern)
    await async_session.flush()
    return mentor, interns


@pytest.fixture
async def intern_for_logged_in_mentor(async_session: AsyncSession, mentor):
    intern = InternFactory(mentor=mentor)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def intern_for_other_mentor(async_session: AsyncSession, default_unit):
    other_mentor = MentorFactory(unit=default_unit)
    intern = InternFactory(mentor=other_mentor)
    if other_mentor not in async_session:
        async_session.add(other_mentor)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def stats_mentor(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def sold_in_jan_intern(async_session: AsyncSession, stats_mentor):
    intern = InternFactory(mentor=stats_mentor, status=InternshipStatus.sold)
    intern.end_date = datetime(2026, 1, 10, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def laid_off_in_jan_intern(async_session: AsyncSession, stats_mentor):
    intern = InternFactory(mentor=stats_mentor, status=InternshipStatus.laid_off)
    intern.end_date = datetime(2026, 1, 20, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def sold_in_feb_intern(async_session: AsyncSession, stats_mentor):
    intern = InternFactory(mentor=stats_mentor, status=InternshipStatus.sold)
    intern.end_date = datetime(2026, 2, 5, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def stats_mentor1(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(email="m1@example.com", unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def stats_mentor2(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(email="m2@example.com", unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def sold_m1_intern(async_session: AsyncSession, stats_mentor1):
    intern = InternFactory(mentor=stats_mentor1, status=InternshipStatus.sold)
    intern.end_date = datetime(2026, 1, 15, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def sold_m2_intern(async_session: AsyncSession, stats_mentor2):
    intern = InternFactory(mentor=stats_mentor2, status=InternshipStatus.sold)
    intern.end_date = datetime(2026, 1, 18, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def prev_period_sold_intern(async_session: AsyncSession, stats_mentor):
    intern = InternFactory(mentor=stats_mentor, status=InternshipStatus.sold)
    intern.end_date = datetime(2025, 12, 10, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def curr_period_sold_intern1(async_session: AsyncSession, stats_mentor):
    intern = InternFactory(mentor=stats_mentor, status=InternshipStatus.sold)
    intern.end_date = datetime(2026, 1, 10, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def curr_period_sold_intern2(async_session: AsyncSession, stats_mentor):
    intern = InternFactory(mentor=stats_mentor, status=InternshipStatus.sold)
    intern.end_date = datetime(2026, 1, 20, tzinfo=timezone.utc).date()
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def snapshot_mentor(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def snapshot_match_intern(async_session: AsyncSession, snapshot_mentor):
    intern = InternFactory(
        mentor=snapshot_mentor,
        status=InternshipStatus.active,
        english_level=EnglishLevel.B1,
        city="Moscow",
        ready_for_sale=True,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def snapshot_wrong_english_intern(async_session: AsyncSession, snapshot_mentor):
    intern = InternFactory(
        mentor=snapshot_mentor,
        status=InternshipStatus.active,
        english_level=EnglishLevel.C1,
        city="Moscow",
        ready_for_sale=True,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def snapshot_wrong_city_intern(async_session: AsyncSession, snapshot_mentor):
    intern = InternFactory(
        mentor=snapshot_mentor,
        status=InternshipStatus.active,
        english_level=EnglishLevel.B1,
        city="London",
        ready_for_sale=True,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def snapshot_wrong_status_intern(async_session: AsyncSession, snapshot_mentor):
    intern = InternFactory(
        mentor=snapshot_mentor,
        status=InternshipStatus.awaited,
        english_level=EnglishLevel.B1,
        city="Moscow",
        ready_for_sale=True,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def snapshot_wrong_ready_intern(async_session: AsyncSession, snapshot_mentor):
    intern = InternFactory(
        mentor=snapshot_mentor,
        status=InternshipStatus.active,
        english_level=EnglishLevel.B1,
        city="Moscow",
        ready_for_sale=False,
    )
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def other_mentor_for_stats(async_session: AsyncSession):
    mentor = MentorFactory(email="other@example.com")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def other_mentor2_for_stats(async_session: AsyncSession):
    mentor = MentorFactory(email="other2@example.com")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor
