"""add english to intern

Revision ID: e9da37f22793
Revises: e7efe0323871
Create Date: 2026-01-09 13:09:35.739548
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e9da37f22793"
down_revision: Union[str, Sequence[str], None] = "e7efe0323871"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ENGLISH_LEVEL_ENUM = postgresql.ENUM(
    "A2", "B1", "B2", "C1", "C2", "other",
    name="english_level",
)

def upgrade() -> None:
    ENGLISH_LEVEL_ENUM.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "intern_profiles",
        sa.Column(
            "english_level",
            ENGLISH_LEVEL_ENUM,
            nullable=False,
            server_default="other",
        ),
    )
    op.add_column(
        "intern_profiles",
        sa.Column(
            "additional_info",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )



def downgrade() -> None:
    op.drop_column("intern_profiles", "additional_info")
    op.drop_column("intern_profiles", "english_level")

    ENGLISH_LEVEL_ENUM.drop(op.get_bind(), checkfirst=True)
