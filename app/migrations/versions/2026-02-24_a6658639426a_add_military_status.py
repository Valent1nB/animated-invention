"""add military status

Revision ID: a6658639426a
Revises: d104d639393b
Create Date: 2026-02-24 13:51:52.656498
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a6658639426a"
down_revision: Union[str, Sequence[str], None] = "d104d639393b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


military_status_enum = postgresql.ENUM(
    "subject_to_conscription",
    "not_subject_to_conscription",
    "possible_call_ups",
    name="military_status",
)


def upgrade() -> None:
    military_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "intern_profiles",
        sa.Column(
            "military_status",
            military_status_enum,
            server_default="not_subject_to_conscription",
            nullable=False,
        ),
    )
    op.add_column(
        "intern_profiles",
        sa.Column("military_occupation_at", sa.Date(), nullable=True),
    )

    op.alter_column("intern_profiles", "military_status", server_default=None)


def downgrade() -> None:
    op.drop_column("intern_profiles", "military_occupation_at")
    op.drop_column("intern_profiles", "military_status")

    military_status_enum.drop(op.get_bind(), checkfirst=True)
