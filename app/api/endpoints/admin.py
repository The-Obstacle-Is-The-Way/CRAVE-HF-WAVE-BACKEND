# File: app/api/endpoints/admin.py
"""
Administrative endpoints for database management and system maintenance.

These endpoints provide direct database fixes and schema management
without relying on dependencies from other modules.
"""
from fastapi import APIRouter
from sqlalchemy import create_engine, text
import alembic.config
import alembic.command
import logging
import os

# Import settings directly (no dependency)
from app.config.settings import Settings

# Configure logging
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()

@router.post("/stamp-db")
def stamp_db():
    """
    Stamp the database to 'head' so Alembic won't try to re-create existing tables.
    """
    # Point this to your alembic.ini
    alembic_cfg = alembic.config.Config("alembic.ini")
    
    # Stamp the DB to the latest revision
    alembic.command.stamp(alembic_cfg, "head")
    
    return {"detail": "Database successfully stamped to 'head'."}

@router.post("/add-missing-column")
def add_missing_column():
    """
    Directly add the missing is_deleted column to the cravings table.
    """
    # Get database connection settings
    settings = Settings()
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.begin() as conn:
            # First check if the column already exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='is_deleted'"
            ))
            
            # If column already exists, we're done
            if result.scalar():
                return {"message": "Column is_deleted already exists"}
            
            # Add the is_deleted column with a default value of false
            conn.execute(text(
                "ALTER TABLE cravings ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL"
            ))
            
            return {"message": "Successfully added is_deleted column"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/add-missing-columns")
def add_missing_columns():
    """
    Add any missing columns to the cravings table.
    """
    # Get database connection settings
    settings = Settings()
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    results = {}
    
    try:
        with engine.begin() as conn:
            # Check for user_id column
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='user_id'"
            ))
            user_id_exists = bool(result.scalar())
            
            if not user_id_exists:
                # Add user_id column with default value
                conn.execute(text(
                    "ALTER TABLE cravings ADD COLUMN user_id INTEGER DEFAULT 1 NOT NULL"
                ))
                results["user_id"] = "Added column"
            else:
                results["user_id"] = "Column already exists"
            
            # Check for updated_at column
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='updated_at'"
            ))
            updated_at_exists = bool(result.scalar())
            
            if not updated_at_exists:
                # Add updated_at column
                conn.execute(text(
                    "ALTER TABLE cravings ADD COLUMN updated_at TIMESTAMP DEFAULT NOW() NOT NULL"
                ))
                
                # Add trigger for automatic updates
                conn.execute(text("""
                    CREATE OR REPLACE FUNCTION update_modified_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = now();
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                    
                    DROP TRIGGER IF EXISTS update_cravings_updated_at ON cravings;
                    
                    CREATE TRIGGER update_cravings_updated_at
                    BEFORE UPDATE ON cravings
                    FOR EACH ROW
                    EXECUTE FUNCTION update_modified_column();
                """))
                
                results["updated_at"] = "Added column and trigger"
            else:
                results["updated_at"] = "Column already exists"
        
        return {
            "success": True,
            "columns_added": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/fix-database")
def fix_database():
    """
    Comprehensive database fix: adds missing columns and updates Alembic state.
    """
    # Step 1: Add missing columns
    columns_result = add_missing_columns()
    
    # Step 2: Stamp the database to head
    stamp_result = stamp_db()
    
    # Return a combined result
    return {
        "columns_operation": columns_result,
        "stamp_operation": stamp_result,
        "message": "Database fix operations completed"
    }

@router.get("/verify-schema")
def verify_schema():
    """
    Verify that the database schema is correctly set up.
    """
    # Get database connection settings
    settings = Settings()
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            # Check for is_deleted column
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='is_deleted'"
            ))
            is_deleted_exists = bool(result.scalar())
            
            # Check for user_id column
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='user_id'"
            ))
            user_id_exists = bool(result.scalar())
            
            # Check for updated_at column
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='updated_at'"
            ))
            updated_at_exists = bool(result.scalar())
            
            return {
                "schema_status": "ok" if (is_deleted_exists and user_id_exists) else "missing_columns",
                "columns": {
                    "is_deleted": is_deleted_exists,
                    "user_id": user_id_exists,
                    "updated_at": updated_at_exists
                }
            }
    except Exception as e:
        return {"error": str(e)}