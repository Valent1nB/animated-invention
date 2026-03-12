from uuid import uuid4

import factory
from faker import Faker
from fastapi_users.password import PasswordHelper

from app.infrastructure.database import User

from .base import BaseFactory

fake = Faker()

password_helper = PasswordHelper()


class UserFactory(BaseFactory):
    class Meta:
        model = User

    id = factory.LazyFunction(uuid4)
    email = factory.Sequence(lambda n: f"employee{n}@example.com")
    hashed_password = factory.LazyFunction(lambda: password_helper.hash("password"))

    is_active = True
    is_superuser = False
    is_verified = True
