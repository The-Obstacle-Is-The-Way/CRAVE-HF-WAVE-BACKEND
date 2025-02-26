"""
Add missing user columns to 'users' table.

We originally only had 'id' and 'email'. This migration adds:
  - password_hash (String, not null)
  - username (String, nullable)
  - created_at (DateTime, default now)
  - updated_at (DateTime, default now)
  - is_active (Boolean, default true)
  - is_deleted (Boolean, default false)

Revision ID: 20250227_add_user_columns
Revises: b98f7a216c5d
Create Date: 2025-02-27 12:34:56
"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = "20250227_add_user_columns"
down_revision: Union[str, None] = "b98f7a216c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add columns to the existing 'users' table
    op.add_column("users", sa.Column("password_hash", sa.String(), nullable=False, server_default=""))
    op.add_column("users", sa.Column("username", sa.String(), nullable=True))
    op.add_column("users", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("users", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"))

def downgrade() -> None:
    # Remove these columns if we revert
    op.drop_column("users", "is_deleted")
    op.drop_column("users", "is_active")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "username")
    op.drop_column("users", "password_hash")
