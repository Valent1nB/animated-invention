"""add unit

Revision ID: d104d639393b
Revises: 9d5600563096
Create Date: 2026-02-03 14:11:31.151374
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd104d639393b'
down_revision: Union[str, Sequence[str], None] = '9d5600563096'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'units',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id', name='pk_units'),
        sa.UniqueConstraint('name', name='uq_units_name'),
    )

    op.execute("""
        INSERT INTO units (id, name)
        VALUES
            (gen_random_uuid(), 'Python'),
            (gen_random_uuid(), 'Java');
    """)

    op.add_column(
        'intern_profiles',
        sa.Column('unit_id', sa.UUID(), nullable=True),
    )
    op.add_column(
        'mentor_profiles',
        sa.Column('unit_id', sa.UUID(), nullable=True),
    )

    op.execute("""
        UPDATE intern_profiles
        SET unit_id = (
            SELECT id FROM units WHERE name = 'Python'
        );
    """)
    op.execute("""
        UPDATE mentor_profiles
        SET unit_id = (
            SELECT id FROM units WHERE name = 'Python'
        );
    """)

    op.alter_column('intern_profiles', 'unit_id', nullable=False)
    op.alter_column('mentor_profiles', 'unit_id', nullable=False)

    op.create_foreign_key(
        'fk_intern_profiles_unit_id_units',
        'intern_profiles',
        'units',
        ['unit_id'],
        ['id'],
        ondelete='RESTRICT',
    )
    op.create_foreign_key(
        'fk_mentor_profiles_unit_id_units',
        'mentor_profiles',
        'units',
        ['unit_id'],
        ['id'],
        ondelete='RESTRICT',
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_mentor_profiles_unit_id_units',
        'mentor_profiles',
        type_='foreignkey',
    )
    op.drop_column('mentor_profiles', 'unit_id')

    op.drop_constraint(
        'fk_intern_profiles_unit_id_units',
        'intern_profiles',
        type_='foreignkey',
    )
    op.drop_column('intern_profiles', 'unit_id')

    op.drop_table('units')
