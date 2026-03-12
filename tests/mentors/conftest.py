import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.mentor import MentorFactory


@pytest.fixture
async def test_mentor(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def other_mentor(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def archived_mentor(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(available=False, available_for_interview=False, unit=default_unit)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def multiple_mentors(async_session: AsyncSession):
    mentors = [MentorFactory() for _ in range(5)]
    for mentor in mentors:
        if mentor not in async_session:
            async_session.add(mentor)
    await async_session.flush()
    return mentors


@pytest.fixture
async def mentor_with_custom_email(async_session: AsyncSession):
    mentor = MentorFactory(email="john.doe@example.com", first_name="John", last_name="Doe")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def available_mentor(async_session: AsyncSession):
    mentor = MentorFactory(available=True)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def unavailable_mentor(async_session: AsyncSession):
    mentor = MentorFactory(available=False)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def mentor_available_for_interview(async_session: AsyncSession):
    mentor = MentorFactory(available_for_interview=True)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def mentor_not_available_for_interview(async_session: AsyncSession):
    mentor = MentorFactory(available_for_interview=False)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def jane_smith_mentor(async_session: AsyncSession):
    mentor = MentorFactory(email="jane.smith@example.com", first_name="Jane", last_name="Smith")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def alice_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Alice", last_name="Wonder")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def bob_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Bob", last_name="Builder")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def charlie_brown_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Charlie", last_name="Brown")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def david_wilson_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="David", last_name="Wilson")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def emma_watson_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Emma", last_name="Watson")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def frank_miller_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Frank", last_name="Miller")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def moscow_mentor(async_session: AsyncSession):
    mentor = MentorFactory(city="Moscow", first_name="Ivan", last_name="Ivanov")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def spb_mentor(async_session: AsyncSession):
    mentor = MentorFactory(city="Saint Petersburg", first_name="Petr", last_name="Petrov")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def zoe_zebra_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Zoe", last_name="Zebra")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def alice_apple_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Alice", last_name="Apple")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def zebra_email_mentor(async_session: AsyncSession):
    mentor = MentorFactory(email="zebra@example.com")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def apple_email_mentor(async_session: AsyncSession):
    mentor = MentorFactory(email="apple@example.com")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def zagreb_mentor(async_session: AsyncSession):
    mentor = MentorFactory(city="Zagreb")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def amsterdam_mentor(async_session: AsyncSession):
    mentor = MentorFactory(city="Amsterdam")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def john_doe_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="John", last_name="Doe", email="john@example.com", available=True)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def john_smith_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="John", last_name="Smith", email="john.smith@example.com", available=False)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def jane_doe_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Jane", last_name="Doe", email="jane@example.com", available=True)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def mentor_available_and_interview(async_session: AsyncSession):
    mentor = MentorFactory(available=True, available_for_interview=True)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def mentor_available_not_interview(async_session: AsyncSession):
    mentor = MentorFactory(available=True, available_for_interview=False)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def mentor_unavailable_and_interview(async_session: AsyncSession):
    mentor = MentorFactory(available=False, available_for_interview=True)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def zoe_zebra_zagreb_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Zoe", last_name="Zebra", city="Zagreb")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def alice_apple_amsterdam_mentor(async_session: AsyncSession):
    mentor = MentorFactory(first_name="Alice", last_name="Apple", city="Amsterdam")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def john_doe_moscow_mentor(async_session: AsyncSession):
    mentor = MentorFactory(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        city="Moscow",
        available=True,
        available_for_interview=True,
    )
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def john_smith_spb_mentor(async_session: AsyncSession):
    mentor = MentorFactory(
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        city="Saint Petersburg",
        available=True,
        available_for_interview=False,
    )
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def jane_doe_moscow_mentor(async_session: AsyncSession):
    mentor = MentorFactory(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        city="Moscow",
        available=True,
        available_for_interview=True,
    )
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor
