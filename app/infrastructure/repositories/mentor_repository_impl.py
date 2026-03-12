from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.list import ListResult
from app.domain.entities.employee.enum import UserRole
from app.domain.entities.employee.mentor import MentorIn, MentorListFilters, MentorOut, MentorUpdate, ShortMentorIn
from app.domain.repositories.mentor_repository import IMentorRepository
from app.infrastructure.builders.mentor_filters import MentorQueryBuilder
from app.infrastructure.database import MentorProfile
from app.infrastructure.database.models.employee import MentorProfile as MentorProfileORM


class MentorRepository(IMentorRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list(self, filters: MentorListFilters, employee: MentorProfile | None = None) -> ListResult[MentorOut]:
        builder = MentorQueryBuilder(filters, employee=employee)

        stmt = builder.build_items_with_total_query()
        result = await self._session.execute(stmt)

        rows = result.all()

        if not rows:
            return ListResult(items=[], total=0)

        items = [MentorOut.model_validate(row[0]) for row in rows]
        total = rows[0][1]

        return ListResult(items=items, total=total)

    async def get_head_mentors(self, unit_id: UUID | None = None) -> ListResult[MentorOut]:
        role_filter = or_(
            MentorProfileORM.role == UserRole.superuser,
            MentorProfileORM.role == UserRole.head_mentor,
        )
        stmt = select(MentorProfileORM, func.count().over().label("total_count")).where(role_filter)
        if unit_id is not None:
            stmt = stmt.where(MentorProfileORM.unit_id == unit_id)

        result = await self._session.execute(stmt)
        rows = result.all()

        if not rows:
            return ListResult(items=[], total=0)

        items = [MentorOut.model_validate(row[0]) for row in rows]
        total = rows[0][1]

        return ListResult(items=items, total=total)

    async def create(self, mentor: MentorIn) -> MentorOut:
        mentor_orm = MentorProfileORM(**mentor.model_dump())
        self._session.add(mentor_orm)

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)

    async def create_without_user(self, data: ShortMentorIn) -> MentorOut:
        mentor = MentorProfileORM(**data.model_dump(), user_id=None)
        self._session.add(mentor)
        await self._session.flush()
        await self._session.refresh(mentor)
        return MentorOut.model_validate(mentor)

    async def get_one(self, mentor_id: UUID) -> MentorOut | None:
        stmt = select(MentorProfileORM).where(MentorProfileORM.id == mentor_id)
        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            return None

        return MentorOut.model_validate(mentor_orm)

    async def get_one_by_email(self, email: str) -> MentorOut | None:
        stmt = select(MentorProfileORM).where(MentorProfileORM.email == email)
        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            return None

        return MentorOut.model_validate(mentor_orm)

    async def update(self, mentor_id: UUID, mentor_update: MentorUpdate) -> MentorOut | None:
        stmt = select(MentorProfileORM).where(MentorProfileORM.id == mentor_id)
        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            return None

        update_dict = mentor_update.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(mentor_orm, key, value)

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)

    async def attach_to_user(self, user_id: UUID, mentor_id: UUID) -> MentorOut:
        stmt = select(MentorProfileORM).where(MentorProfileORM.id == mentor_id)
        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one()

        mentor_orm.user_id = user_id

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)

    async def archive(self, mentor_id: UUID) -> MentorOut | None:
        stmt = (
            select(MentorProfileORM)
            .where(MentorProfileORM.id == mentor_id)
            .options(selectinload(MentorProfileORM.user))
        )

        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            return None

        mentor_orm.available = False
        mentor_orm.available_for_interview = False

        if mentor_orm.user is not None:
            mentor_orm.user.is_active = False

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)

    async def recover(self, mentor_id: UUID) -> MentorOut | None:
        stmt = (
            select(MentorProfileORM)
            .where(MentorProfileORM.id == mentor_id)
            .options(selectinload(MentorProfileORM.user))
        )

        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            return None

        mentor_orm.available = True

        if mentor_orm.user is not None:
            mentor_orm.user.is_active = True

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)

    async def upload_avatar(self, mentor_id: UUID, avatar_key: str) -> MentorOut:
        stmt = select(MentorProfileORM).where(MentorProfileORM.id == mentor_id)
        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            raise ValueError("Mentor not found")

        mentor_orm.avatar_key = avatar_key

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)

    async def remove_avatar(self, mentor_id: UUID) -> MentorOut:
        stmt = select(MentorProfileORM).where(MentorProfileORM.id == mentor_id)
        result = await self._session.execute(stmt)
        mentor_orm = result.scalar_one_or_none()

        if mentor_orm is None:
            raise ValueError("Mentor not found")

        mentor_orm.avatar_key = ""

        await self._session.flush()
        await self._session.refresh(mentor_orm)

        return MentorOut.model_validate(mentor_orm)
