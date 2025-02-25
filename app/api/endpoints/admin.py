# File: app/api/endpoints/admin.py
"""
Temporary admin endpoint to stamp the DB to the latest migration.
Use this only once if your production DB is already up to date.
"""
from fastapi import APIRouter
import alembic.config
import alembic.command

router = APIRouter()

@router.post("/stamp-db")
def stamp_db():
    """
    Stamp the DB to 'head' so Alembic won't try to re-create existing tables.
    """
    # Point this to your alembic.ini (adjust path if needed).
    alembic_cfg = alembic.config.Config("alembic.ini")
    
    # Stamp the DB to the latest revision.
    alembic.command.stamp(alembic_cfg, "head")
    
    return {"detail": "Database successfully stamped to 'head'."}