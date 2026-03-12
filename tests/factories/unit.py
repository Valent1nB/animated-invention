from uuid import uuid4

import factory

from app.infrastructure.database.models.unit import Unit

from .base import BaseFactory


class UnitFactory(BaseFactory):
    class Meta:
        model = Unit

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Unit {n}")
