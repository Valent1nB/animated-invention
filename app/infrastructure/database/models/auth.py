from typing import TYPE_CHECKING, AsyncGenerator
from uuid import UUID, uuid4

from fastapi import Depends
from fastapi_users_db_sqlalchemy import (
    GUID,
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import ForeignKey, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.infrastructure.database.models import Base
from app.presentation.dependencies.db import get_async_session

if TYPE_CHECKING:
    from app.infrastructure.database.models.employee import MentorProfile


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    @declared_attr
    def user_id(cls) -> Mapped[GUID]:  # type: ignore
        return mapped_column(GUID, ForeignKey("users.id", ondelete="cascade"), nullable=False)


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid4)

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined", cascade="all, delete-orphan"
    )
    mentor_profile: Mapped["MentorProfile"] = relationship(
        "MentorProfile", back_populates="user", lazy="joined", uselist=False
    )

    @property
    def employee_id(self) -> UUID | None:
        return self.mentor_profile.id if self.mentor_profile else None

    def __repr__(self) -> str:
        return f"User(id={self.id}, employee={self.employee_id})"


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)
