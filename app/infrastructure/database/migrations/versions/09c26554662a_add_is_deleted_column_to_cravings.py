"""Add is_deleted column to cravings

Revision ID: 09c26554662a
Revises: 200c7d532370
Create Date: 2025-02-25 16:53:36.946176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '09c26554662a'
down_revision: Union[str, None] = '200c7d532370'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the is_deleted column to the cravings table.
    op.add_column('cravings', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    # Drop the is_deleted column from the cravings table.
    op.drop_column('cravings', 'is_deleted')