from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, PositiveInt, computed_field

from app.domain.entities.unit.unit import UnitOut
from app.infrastructure.repositories.media_repository_impl import media_repo


class ShortEmployeeOut(BaseModel):
    id: UUID
    hrm_id: PositiveInt | None = None
    unit_id: UUID
    first_name: str
    last_name: str
    avatar_key: str
    email: EmailStr

    @computed_field  # type: ignore[prop-decorator]
    @property
    def image(self) -> str | None:
        if not self.avatar_key:
            return None

        return media_repo.get_presigned_url(self.avatar_key)

    model_config = ConfigDict(from_attributes=True)


class EmployeeOut(ShortEmployeeOut):
    user_id: UUID | None = None
    city: str
    unit: UnitOut

    model_config = ConfigDict(from_attributes=True)


class EmployeeIn(BaseModel):
    hrm_id: PositiveInt | None = None
    first_name: str
    last_name: str
    email: EmailStr
    city: str = ""


class EmployeeUpdate(BaseModel):
    hrm_id: PositiveInt | None = None
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None

    model_config = ConfigDict(from_attributes=True)
