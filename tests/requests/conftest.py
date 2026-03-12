import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.employee.enum import Role, RequestStatus, RequestTopic
from tests.factories.intern import InternFactory
from tests.factories.mentor import MentorFactory
from tests.factories.request import RequestFactory


@pytest.fixture
async def test_request(async_session: AsyncSession, default_unit):
    requester = MentorFactory(role=Role.mentor, unit=default_unit)
    receiver = MentorFactory(role=Role.head_mentor, unit=default_unit)
    if requester not in async_session:
        async_session.add(requester)
    if receiver not in async_session:
        async_session.add(receiver)
    await async_session.flush()

    request = RequestFactory(requester=requester, receiver=receiver)
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_head_mentor_for_request(async_session: AsyncSession, default_unit):
    head_mentor = MentorFactory(
        role=Role.head_mentor,
        email="head_mentor_for_request@example.com",
        unit=default_unit,
    )
    if head_mentor not in async_session:
        async_session.add(head_mentor)
    await async_session.flush()
    return head_mentor


@pytest.fixture
async def test_mentor_for_request(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(
        role=Role.mentor,
        email="mentor_for_request@example.com",
        unit=default_unit,
    )
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def test_request_created(async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        status=RequestStatus.created,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_in_progress(async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        status=RequestStatus.in_progress,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_completed(async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        status=RequestStatus.completed,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_canceled(async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        status=RequestStatus.canceled,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_give_cv(async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        topic=RequestTopic.give_cv,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_add_to_checks(
    async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request
):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        topic=RequestTopic.add_to_checks,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_create_aws_acc(
    async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request
):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        topic=RequestTopic.create_aws_acc,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def test_request_more_interns_needed(
    async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request
):
    request = RequestFactory(
        requester=test_mentor_for_request,
        receiver=test_head_mentor_for_request,
        topic=RequestTopic.more_interns_needed,
    )
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


@pytest.fixture
async def multiple_requests(async_session: AsyncSession, test_mentor_for_request, test_head_mentor_for_request):
    requests = [
        RequestFactory(requester=test_mentor_for_request, receiver=test_head_mentor_for_request) for _ in range(5)
    ]
    for request in requests:
        if request not in async_session:
            async_session.add(request)
    await async_session.flush()
    return requests


@pytest.fixture
async def other_mentor_for_request(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(
        role=Role.mentor,
        email="other_mentor@example.com",
        unit=default_unit,
    )
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def other_head_mentor_for_request(async_session: AsyncSession, default_unit):
    head_mentor = MentorFactory(
        role=Role.head_mentor,
        email="other_head_mentor@example.com",
        unit=default_unit,
    )
    if head_mentor not in async_session:
        async_session.add(head_mentor)
    await async_session.flush()
    return head_mentor


@pytest.fixture
async def request_for_other_mentor(async_session: AsyncSession, other_mentor_for_request, test_head_mentor_for_request):
    request = RequestFactory(requester=other_mentor_for_request, receiver=test_head_mentor_for_request)
    if request not in async_session:
        async_session.add(request)
    await async_session.flush()
    return request


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
