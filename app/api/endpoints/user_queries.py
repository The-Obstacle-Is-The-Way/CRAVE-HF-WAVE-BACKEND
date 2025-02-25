# File: app/api/endpoints/user_queries.py
"""
Endpoints for updating and deleting cravings.
Follows clean architecture with dependency injection.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Repository for CRUD operations on cravings and dependency for DB sessions.
from app.infrastructure.database.repository import CravingRepository, get_db

router = APIRouter()

# Pydantic model for updating a craving.
class CravingUpdate(BaseModel):
    description: str | None = None
    intensity: int | None = None
    # Add additional fields as needed

@router.put("/api/cravings/{craving_id}", tags=["Cravings"])
async def update_craving(craving_id: int, craving_update: CravingUpdate, db: Session = Depends(get_db)):
    """
    Update an existing craving.

    1. Fetch the current craving via CravingRepository.
    2. If not found, raise a 404 error.
    3. Otherwise, update only the fields provided.
    4. Return the updated craving.
    """
    repository = CravingRepository(db)
    existing = repository.get_craving_by_id(craving_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Craving not found")
    updated = repository.update_craving(craving_id, craving_update.dict(exclude_unset=True))
    return updated

@router.delete("/api/cravings/{craving_id}", tags=["Cravings"])
async def delete_craving(craving_id: int, db: Session = Depends(get_db)):
    """
    Soft-delete an existing craving.

    1. Fetch the craving record.
    2. If not found, raise a 404 error.
    3. Otherwise, mark it as deleted.
    4. Return a confirmation message.
    """
    repository = CravingRepository(db)
    existing = repository.get_craving_by_id(craving_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Craving not found")
    repository.delete_craving(craving_id)
    return {"detail": "Craving deleted successfully"}