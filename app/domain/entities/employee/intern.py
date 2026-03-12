from __future__ import annotations

from datetime import date
from typing import Literal, Sequence
from uuid import UUID

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from app.common.date import DateRange
from app.common.pagination import Pagination
from app.domain.entities.employee.employee import EmployeeIn, EmployeeOut, EmployeeUpdate
from app.domain.entities.employee.enum import (
    EmploymentStatus,
    EnglishLevel,
    InternshipStatus,
    InternSort,
    MilitaryStatus,
)
from app.domain.entities.employee.mentor import ShortMentorOut


class InternOut(EmployeeOut):
    mentor: ShortMentorOut

    start_date: date | None
    end_date: date | None

    status: InternshipStatus

    notes: str
    birth_date: date | None
    age: int | None

    mentor_feedback: str
    ready_for_sale: bool

    additional_occupation: str
    employment_status: EmploymentStatus

    university_name: str
    university_course: int | None
    english_level: EnglishLevel
    additional_info: str

    military_status: MilitaryStatus
    military_occupation_at: date | None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def internship_length_parts(self) -> InternshipLengthParts | None:
        if not self.start_date:
            return None

        end = self.end_date or date.today()
        rd = relativedelta(end, self.start_date)
        return InternshipLengthParts(years=rd.years, months=rd.months, days=rd.days)


class InternshipLengthParts(BaseModel):
    years: int
    months: int
    days: int


class InternIn(EmployeeIn):
    unit_id: UUID
    mentor_id: UUID

    start_date: date | None = None
    end_date: date | None = None

    status: InternshipStatus = InternshipStatus.awaited

    notes: str = ""
    birth_date: date | None = None

    mentor_feedback: str = ""
    ready_for_sale: bool = False

    additional_occupation: str = ""
    employment_status: EmploymentStatus = EmploymentStatus.other

    university_name: str = ""
    university_course: int | None = None

    english_level: EnglishLevel
    additional_info: str = ""

    military_status: MilitaryStatus = MilitaryStatus.subject_to_conscription
    military_occupation_at: date | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_birth_date(self):
        if self.birth_date is not None and self.birth_date >= date.today():
            raise ValueError("Birth date cannot be today or in the future")
        return self


class InternUpdateMentor(EmployeeUpdate):
    start_date: date | None = None
    end_date: date | None = None

    status: InternshipStatus | None = None
    birth_date: date | None = None

    mentor_feedback: str | None = None
    ready_for_sale: bool | None = None

    additional_occupation: str | None = None
    employment_status: EmploymentStatus | None = None

    university_name: str | None = None
    university_course: int | None = None

    english_level: EnglishLevel | None = None
    additional_info: str | None = None

    military_status: MilitaryStatus | None = None
    military_occupation_at: date | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_birth_date(self):
        if self.birth_date is not None and self.birth_date >= date.today():
            raise ValueError("Birth date cannot be today or in the future")
        return self


class InternUpdate(InternUpdateMentor):
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class ReassignMentorRequest(BaseModel):
    new_mentor_id: UUID


class Order(BaseModel):
    by: InternSort = InternSort.full_name
    direction: Literal["asc", "desc"] = "asc"


class InternListFilters(BaseModel):
    search: str | None = None

    status: list[InternshipStatus] | None = None
    mentor_id: UUID | None = None
    unit_id: UUID | None = None
    employment_status: list[EmploymentStatus] | None = None
    english_level: list[EnglishLevel] | None = None
    ready_for_sale: bool | None = None
    military_status: list[MilitaryStatus] | None = None

    order: Order = Order()
    pagination: Pagination = Pagination()


class InternListResponse(BaseModel):
    items: Sequence[InternOut]
    total: int
    limit: int
    offset: int


class InternStatsFilters(BaseModel):
    statuses: set[InternshipStatus] | None = None
    period: DateRange
    mentor_id: UUID | None = None
    unit_id: UUID | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_statuses(self) -> "InternStatsFilters":
        allowed = {InternshipStatus.sold, InternshipStatus.laid_off}
        if self.statuses is None:
            self.statuses = allowed
            return self

        if not self.statuses.issubset(allowed):
            raise ValueError("Only sold and laid_off statuses are allowed for period stats")
        return self


class InternSnapshotFilters(BaseModel):
    statuses: set[InternshipStatus] | None = None
    english_levels: set[EnglishLevel] | None = None
    cities: set[str] | None = None
    ready_for_sale: bool | None = None
    mentor_id: UUID | None = None
    unit_id: UUID | None = None

    model_config = ConfigDict(extra="forbid")


class InternStatsOut(BaseModel):
    total: int
    by_status: dict[InternshipStatus, int]
    interns_by_status: dict[InternshipStatus, list[InternOut]] = {}


class InternStatsComparisonFilters(BaseModel):
    statuses: set[InternshipStatus] | None = None
    current_period: DateRange
    previous_period: DateRange
    mentor_id: UUID | None = None
    unit_id: UUID | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_statuses(self) -> "InternStatsComparisonFilters":
        allowed = {InternshipStatus.sold, InternshipStatus.laid_off}
        if self.statuses is None:
            self.statuses = allowed
            return self

        if not self.statuses.issubset(allowed):
            raise ValueError("Only sold and laid_off statuses are allowed for period stats")
        return self


class InternStatsComparisonOut(BaseModel):
    current: InternStatsOut
    previous: InternStatsOut
    absolute_change: int
    percent_change: float | None


class MentorWithInterns(BaseModel):
    mentor: ShortMentorOut
    interns: Sequence[InternOut]
    total: int


class InternGroupedByMentorResponse(BaseModel):
    groups: Sequence[MentorWithInterns]
    total_mentors: int
    total_interns: int
