"""ticket created_at with timezone

Revision ID: ef2ad31b8ed1
Revises: e3340d36f75b
Create Date: 2026-10-08 20:23:02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef2ad31b8ed1'
down_revision: Union[str, Sequence[str], None] = 'e3340d36f75b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Existing values were written in UTC: convert them as UTC, not as the
    # session time zone, so no ticket changes its moment in time.
    op.alter_column(
        'ticket',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text('now()'),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'ticket',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=False,
        existing_server_default=sa.text('now()'),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
    )
