from uuid import uuid4

import factory

from app.domain.entities.employee.enum import Role, RequestStatus, RequestTopic
from app.infrastructure.database import Request

from .base import BaseFactory
from .mentor import MentorFactory


class RequestFactory(BaseFactory):
    class Meta:
        model = Request

    id = factory.LazyFunction(uuid4)

    requester = factory.SubFactory(MentorFactory)
    requester_id = factory.SelfAttribute("requester.id")

    receiver = factory.SubFactory(MentorFactory, role=Role.head_mentor)
    receiver_id = factory.SelfAttribute("receiver.id")

    status = RequestStatus.created
    topic = RequestTopic.other
    intern_id = None
    extra_info = ""
    comment_from_receiver = ""
    closed_at = None
