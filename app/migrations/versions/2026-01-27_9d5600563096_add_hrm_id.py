"""add hrm id

Revision ID: 9d5600563096
Revises: c146ed873fc8
Create Date: 2026-01-27 16:54:05.298840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d5600563096'
down_revision: Union[str, Sequence[str], None] = 'c146ed873fc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('intern_profiles', sa.Column('hrm_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(
        'uq_intern_profiles_hrm_id',
        'intern_profiles',
        ['hrm_id']
    )

    op.add_column('mentor_profiles', sa.Column('hrm_id', sa.Integer(), nullable=True))
    op.create_unique_constraint(
        'uq_mentor_profiles_hrm_id',
        'mentor_profiles',
        ['hrm_id']
    )

def downgrade() -> None:
    op.drop_constraint('uq_mentor_profiles_hrm_id', 'mentor_profiles', type_='unique')
    op.drop_column('mentor_profiles', 'hrm_id')

    op.drop_constraint('uq_intern_profiles_hrm_id', 'intern_profiles', type_='unique')
    op.drop_column('intern_profiles', 'hrm_id')
