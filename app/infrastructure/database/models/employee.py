from datetime import date, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text, case, func, select, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, column_property, declared_attr, mapped_column, relationship

from app.domain.entities.employee.enum import (
    Role,
    EmploymentStatus,
    EnglishLevel,
    InternshipStatus,
    MilitaryStatus,
    UserRole,
)
from app.infrastructure.database import Base, User

if TYPE_CHECKING:
    from app.infrastructure.database.models.request import Request


class Employee(Base):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)

    hrm_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)

    unit_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=False,
    )

    @declared_attr
    def unit(cls):
        return relationship("Unit", lazy="selectin")

    first_name: Mapped[str] = mapped_column(String, nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String, nullable=False, default="")
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    avatar_key: Mapped[str] = mapped_column(String, nullable=False, default="")
    city: Mapped[str] = mapped_column(String, nullable=False, default="")

    def __repr__(self) -> str:
        return f"Employee(id={self.id}, email={self.email}, name={self.first_name, self.last_name}"


class InternProfile(Employee):
    __tablename__ = "intern_profiles"

    start_date: Mapped[date | None] = mapped_column(nullable=True)
    end_date: Mapped[date | None] = mapped_column(nullable=True)

    status: Mapped[InternshipStatus] = mapped_column(
        Enum(InternshipStatus, name="internship_status"),
        nullable=False,
        default=InternshipStatus.awaited,
    )

    mentor_id: Mapped[UUID] = mapped_column(
        ForeignKey("mentor_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mentor: Mapped["MentorProfile"] = relationship(
        "MentorProfile",
        back_populates="interns",
        lazy="selectin",
    )

    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    additional_occupation: Mapped[str] = mapped_column(Text, nullable=False, default="")

    employment_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus, name="employment_status"),
        nullable=False,
        default=EmploymentStatus.other,
    )

    mentor_feedback: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")

    ready_for_sale: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    university_name: Mapped[str] = mapped_column(nullable=False, default="")
    university_course: Mapped[int | None] = mapped_column(Integer, nullable=True)

    english_level: Mapped[EnglishLevel] = mapped_column(
        Enum(EnglishLevel, name="english_level"),
        nullable=False,
        default=EnglishLevel.other,
        server_default=EnglishLevel.other,
    )
    additional_info: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")

    military_status: Mapped[MilitaryStatus] = mapped_column(
        Enum(MilitaryStatus, name="military_status"),
        nullable=False,
        default=MilitaryStatus.not_subject_to_conscription,
        server_default="not_subject_to_conscription",
    )
    military_occupation_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    age: Mapped[int | None] = column_property(
        case(
            (
                birth_date.isnot(None),
                func.extract("year", func.age(func.current_date(), birth_date)),
            ),
            else_=None,
        )
    )

    internship_length: Mapped[timedelta | None] = column_property(
        case(
            (
                start_date.isnot(None),
                func.coalesce(end_date, func.current_date()) - start_date,
            ),
            else_=None,
        )
    )


class MentorProfile(Employee):
    __tablename__ = "mentor_profiles"

    role: Mapped[UserRole] = mapped_column(ENUM(Role), nullable=False, default=Role.mentor)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    available_for_interview: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    user_id: Mapped[UUID | None] = mapped_column(PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user: Mapped[User | None] = relationship("User", back_populates="mentor_profile", single_parent=True)

    interns: Mapped[list["InternProfile"]] = relationship(
        "InternProfile",
        back_populates="mentor",
    )

    requests_sent: Mapped[list["Request"]] = relationship(
        "Request",
        foreign_keys="Request.requester_id",
        back_populates="requester",
    )

    requests_received: Mapped[list["Request"]] = relationship(
        "Request",
        foreign_keys="Request.receiver_id",
        back_populates="receiver",
    )

    @declared_attr
    def interns_active(cls) -> Mapped[int]:
        return column_property(
            select(func.count(InternProfile.id))
            .where(
                InternProfile.mentor_id == cls.id,
                InternProfile.status.in_(
                    [
                        InternshipStatus.awaited,
                        InternshipStatus.active,
                        InternshipStatus.for_sale,
                        InternshipStatus.paused,
                    ]
                ),
            )
            .correlate_except(InternProfile)
            .scalar_subquery()
        )
