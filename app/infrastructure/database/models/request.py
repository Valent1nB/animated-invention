from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.employee.enum import RequestStatus, RequestTopic
from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.employee import InternProfile, MentorProfile


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)

    requester_id: Mapped[UUID] = mapped_column(
        ForeignKey("mentor_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    requester: Mapped["MentorProfile"] = relationship(
        "MentorProfile",
        foreign_keys=[requester_id],
        back_populates="requests_sent",
        lazy="selectin",
    )

    receiver_id: Mapped[UUID] = mapped_column(
        ForeignKey("mentor_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    receiver: Mapped["MentorProfile"] = relationship(
        "MentorProfile",
        foreign_keys=[receiver_id],
        back_populates="requests_received",
        lazy="selectin",
    )

    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status"),
        nullable=False,
        default=RequestStatus.created,
    )

    topic: Mapped[RequestTopic] = mapped_column(
        Enum(RequestTopic, name="request_topic"),
        nullable=False,
    )

    intern_id: Mapped[UUID | None] = mapped_column(
        PGUUID,
        ForeignKey("intern_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    intern: Mapped["InternProfile | None"] = relationship(
        "InternProfile",
        foreign_keys=[intern_id],
        lazy="selectin",
    )

    extra_info: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")

    comment_from_receiver: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")

    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"Request(id={self.id},"
            f" requester_id={self.requester_id},"
            f" receiver_id={self.receiver_id},"
            f" status={self.status})"
        )
