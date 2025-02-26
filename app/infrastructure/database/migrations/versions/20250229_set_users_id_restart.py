"""
Set users.id restart value to MAX(id) + 1

Revision ID: 20250229_set_users_id_restart
Revises: 20250228_fix_users_id
Create Date: 2025-02-29 12:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20250229_set_users_id_restart"
down_revision = "20250228_fix_users_id"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
    DO $$
    DECLARE 
        max_id integer;
    BEGIN
        SELECT COALESCE(MAX(id), 0) + 1 INTO max_id FROM users;
        EXECUTE 'ALTER TABLE users ALTER COLUMN id RESTART WITH ' || max_id;
    END $$;
    """)

def downgrade() -> None:
    # In downgrade, you could restart with 1, but this is rarely needed.
    op.execute("ALTER TABLE users ALTER COLUMN id RESTART WITH 1")
