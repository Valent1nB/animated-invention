from typing import Literal, Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field

from app.application.services.permission_service import PermissionService
from app.common.pagination import Pagination
from app.domain.entities.employee.employee import EmployeeIn, EmployeeOut, EmployeeUpdate, ShortEmployeeOut
from app.domain.entities.employee.enum import Role, MentorSort, Permission, UserRole


class ShortMentorOut(ShortEmployeeOut):
    pass


class MentorOut(EmployeeOut):
    role: Role
    available: bool
    available_for_interview: bool
    interns_active: int


class FullMentorOut(MentorOut):
    @computed_field  # type: ignore[prop-decorator]
    @property
    def permissions(self) -> list[Permission]:
        role = UserRole(self.role)
        return list(PermissionService.get_permissions(role))


class ShortMentorIn(EmployeeIn):
    unit_id: UUID
    available: bool = True
    available_for_interview: bool = True
    role: Literal[Role.mentor] = Role.mentor


class MentorIn(ShortMentorIn):
    user_id: UUID | None = None

    model_config = ConfigDict(extra="forbid")


class MentorUpdate(EmployeeUpdate):
    available_for_interview: bool | None = None
    city: str | None = None

    model_config = ConfigDict(extra="forbid")


class Order(BaseModel):
    by: MentorSort = MentorSort.full_name
    direction: Literal["asc", "desc"] = "asc"


class MentorListFilters(BaseModel):
    search: str | None = None

    available: bool | None = None
    available_for_interview: bool | None = None
    role: list[Role] | None = None
    unit_id: UUID | None = None

    order: Order = Order()
    pagination: Pagination = Pagination()


class MentorListResponse(BaseModel):
    items: Sequence[MentorOut]
    total: int
    limit: int
    offset: int
