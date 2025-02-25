# File: app/api/endpoints/admin.py
"""
Administrative endpoints for database management and system maintenance.

These endpoints are designed for administrative use only and should be secured or
removed in production environments after initial setup. They provide functionality
for database migration management, schema verification, and emergency fixes.

Following Clean Architecture principles, this module:
- Keeps business logic separate from framework code
- Uses dependency injection for database access
- Maintains clear separation of concerns
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import alembic.config
import alembic.command
import logging

# Import settings and database session from appropriate modules
from app.config.settings import Settings
from app.infrastructure.database.session import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()

@router.post("/stamp-db")
def stamp_db():
    """
    Stamp the database to 'head' so Alembic won't try to re-create existing tables.
    
    This endpoint tells Alembic that the database is at the latest migration version,
    without actually running any migrations. Use this only when the database schema
    is already correctly set up but Alembic's migration tracking is out of sync.
    
    Returns:
        dict: A message indicating the operation was successful
    """
    # Point this to your alembic.ini (adjust path if needed)
    alembic_cfg = alembic.config.Config("alembic.ini")
    
    # Stamp the DB to the latest revision
    logger.info("Stamping database to HEAD revision")
    alembic.command.stamp(alembic_cfg, "head")
    
    return {"detail": "Database successfully stamped to 'head'."}

@router.post("/run-migrations")
def run_migrations():
    """
    Run all pending Alembic migrations to bring the database schema up to date.
    
    This endpoint executes all migrations that haven't yet been applied to the database.
    It's useful when automatic migrations aren't running during deployment.
    
    Returns:
        dict: A message indicating the operation's result
    """
    try:
        # Point this to your alembic.ini
        alembic_cfg = alembic.config.Config("alembic.ini")
        
        # Run all migrations up to head
        logger.info("Running database migrations to HEAD revision")
        alembic.command.upgrade(alembic_cfg, "head")
        
        return {"detail": "Migrations successfully applied."}
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@router.post("/add-missing-column")
def add_missing_column():
    """
    Directly add the missing is_deleted column to the cravings table.
    
    This endpoint bypasses Alembic to directly execute the SQL needed to add
    the is_deleted column. It's intended as an emergency fix when migrations
    aren't working properly.
    
    Returns:
        dict: A message indicating the operation's result
    """
    # Get database connection settings
    settings = Settings()
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            # First check if the column already exists
            logger.info("Checking if is_deleted column exists")
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='is_deleted'"
            ))
            
            # If column already exists, we're done
            if result.scalar():
                logger.info("Column is_deleted already exists")
                return {"message": "Column is_deleted already exists"}
            
            # Add the is_deleted column with a default value of false
            logger.info("Adding is_deleted column to cravings table")
            conn.execute(text(
                "ALTER TABLE cravings ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL"
            ))
            conn.commit()
            
            return {"message": "Successfully added is_deleted column"}
    except Exception as e:
        logger.error(f"Error adding column: {str(e)}")
        return {"error": str(e)}

@router.post("/fix-database")
def fix_database():
    """
    Comprehensive database fix: adds missing columns and updates Alembic state.
    
    This endpoint combines multiple database fixes into a single operation:
    1. Directly adds the is_deleted column if it's missing
    2. Stamps the database to tell Alembic it's up to date
    
    Returns:
        dict: A summary of the operations performed
    """
    logger.info("Starting comprehensive database fix")
    
    # Step 1: Add missing column directly
    column_result = add_missing_column()
    
    # Step 2: Stamp the database to head
    stamp_result = stamp_db()
    
    # Return a combined result
    return {
        "column_operation": column_result,
        "stamp_operation": stamp_result,
        "message": "Database fix operations completed"
    }

@router.get("/verify-schema")
def verify_schema(db: Session = Depends(get_db)):
    """
    Verify that the database schema is correctly set up.
    
    This endpoint checks for critical columns needed by the application
    and reports their status.
    
    Args:
        db: SQLAlchemy database session (injected)
        
    Returns:
        dict: A report of the database schema status
    """
    try:
        # Check for is_deleted column
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='cravings' AND column_name='is_deleted'"
        ))
        is_deleted_exists = bool(result.scalar())
        
        # Check for other critical columns (add as needed)
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='cravings' AND column_name='updated_at'"
        ))
        updated_at_exists = bool(result.scalar())
        
        return {
            "schema_status": "ok" if is_deleted_exists else "missing_columns",
            "columns": {
                "is_deleted": is_deleted_exists,
                "updated_at": updated_at_exists
            }
        }
    except Exception as e:
        logger.error(f"Error verifying schema: {str(e)}")
        return {"error": str(e)}