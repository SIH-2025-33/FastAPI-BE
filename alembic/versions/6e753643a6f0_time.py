"""Time

Revision ID: 6e753643a6f0
Revises: d5980a093659
Create Date: 2025-09-20 17:53:57.186939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e753643a6f0'
down_revision: Union[str, Sequence[str], None] = 'd5980a093659'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'complaint', 'timestamp',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using='"timestamp"::timestamp'
    )
    op.alter_column(
        'data_collector', 'timestamp',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using='"timestamp"::timestamp'
    )
    op.alter_column(
        'trip', 'start_time',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using='"start_time"::timestamp'
    )
    op.alter_column(
        'trip', 'end_time',
        existing_type=sa.VARCHAR(),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using='"end_time"::timestamp'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'trip', 'end_time',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=False
    )
    op.alter_column(
        'trip', 'start_time',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=False
    )
    op.alter_column(
        'data_collector', 'timestamp',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
    op.alter_column(
        'complaint', 'timestamp',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
