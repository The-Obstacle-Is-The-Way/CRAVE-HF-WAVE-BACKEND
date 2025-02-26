#app/infrastructure/database/migrations/versions/20250301_add_display_name_avatar_url.py
"""
Add display_name and avatar_url columns to users

Revision ID: 20250301_add_display_name_avatar_url
Revises: 20250229_set_users_id_restart
Create Date: 2025-03-01 10:00:00
"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = "20250301_add_display_name_avatar_url"
down_revision: Union[str, None] = "20250229_set_users_id_restart"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add two new columns, 'display_name' and 'avatar_url', to the 'users' table.
    Both are nullable. No default values are set.
    """
    op.add_column(
        "users",
        sa.Column("display_name", sa.String(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("avatar_url", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """
    Remove the 'display_name' and 'avatar_url' columns from the 'users' table.
    """
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "display_name")