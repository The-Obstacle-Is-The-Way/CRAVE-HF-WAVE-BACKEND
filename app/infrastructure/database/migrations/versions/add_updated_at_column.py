# File: app/infrastructure/database/migrations/versions/add_updated_at_column.py
"""Add updated_at column to cravings

Revision ID: b98f7a216c5d
Revises: 09c26554662a
Create Date: 2025-02-25 18:42:12.235764

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b98f7a216c5d'
down_revision: Union[str, None] = '09c26554662a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    Add updated_at column to cravings table with default value of created_at.
    This ensures all existing records have a valid updated_at value.
    """
    # First add the column with NULL allowed temporarily
    op.add_column('cravings', 
                 sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Update existing rows to set updated_at = created_at
    op.execute("UPDATE cravings SET updated_at = created_at")
    
    # Now make the column NOT NULL
    op.alter_column('cravings', 'updated_at', nullable=False)
    
    # Add a trigger to automatically update this column
    op.execute("""
        CREATE OR REPLACE FUNCTION update_modified_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_cravings_updated_at
        BEFORE UPDATE ON cravings
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    """)

def downgrade() -> None:
    """
    Remove updated_at column and related trigger.
    """
    # Drop the trigger first
    op.execute("DROP TRIGGER IF EXISTS update_cravings_updated_at ON cravings")
    op.execute("DROP FUNCTION IF EXISTS update_modified_column()")
    
    # Then drop the column
    op.drop_column('cravings', 'updated_at')