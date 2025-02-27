#/app/infrastructure/database/migrations/versions/200c7d532370_initial_tables_users_cravings.py
"""
Initial tables: users & cravings

Revision ID: 200c7d532370
Revises:
Create Date: 2025-02-22 21:32:31.338366
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "200c7d532370"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"], unique=False)

    op.create_table(
        "cravings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("intensity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_cravings_id", "cravings", ["id"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_cravings_id", table_name="cravings")
    op.drop_table("cravings")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
