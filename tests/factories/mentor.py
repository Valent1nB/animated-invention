from uuid import uuid4

import factory

from app.domain.entities.employee.enum import Role
from app.infrastructure.database import MentorProfile

from .auth import UserFactory
from .base import BaseFactory
from .unit import UnitFactory


class MentorFactory(BaseFactory):
    class Meta:
        model = MentorProfile

    id = factory.LazyFunction(uuid4)

    unit = factory.SubFactory(UnitFactory)
    unit_id = factory.LazyAttribute(lambda o: o.unit.id)
    hrm_id = factory.Sequence(lambda n: n + 1)
    role = Role.mentor
    available = True
    available_for_interview = True
    city = factory.Faker("city")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"employee{n}@example.com")
    avatar_key = None

    user = factory.SubFactory(UserFactory, email=factory.SelfAttribute("..email"))
