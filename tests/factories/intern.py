from datetime import date
from uuid import uuid4

import factory

from app.domain.entities.employee.enum import EmploymentStatus, InternshipStatus, MilitaryStatus
from app.infrastructure.database.models.employee import InternProfile

from .base import BaseFactory
from .mentor import MentorFactory


class InternFactory(BaseFactory):
    class Meta:
        model = InternProfile

    id = factory.LazyFunction(uuid4)

    hrm_id = factory.Sequence(lambda n: n + 1000 if n % 10 != 0 else None)  # Some interns may have None hrm_id
    mentor = factory.SubFactory(MentorFactory)
    mentor_id = factory.LazyAttribute(lambda obj: obj.mentor.id)
    unit_id = factory.LazyAttribute(
        lambda obj: getattr(obj.mentor, "unit_id", None) or getattr(obj.mentor.unit, "id", None)
    )

    start_date: date | None = None
    end_date: date | None = None
    status = InternshipStatus.awaited
    notes = ""
    birth_date: date | None = None
    additional_occupation = ""
    employment_status = EmploymentStatus.other
    university_name = ""
    university_course = None
    military_status = MilitaryStatus.subject_to_conscription
    military_occupation_at: date | None = None

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"intern{n}@example.com")
    avatar_key = None
    city = factory.Faker("city")
