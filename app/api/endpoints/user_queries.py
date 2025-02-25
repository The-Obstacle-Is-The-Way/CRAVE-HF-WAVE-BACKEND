# File: app/api/endpoints/user_queries.py
"""
Endpoints for updating and deleting cravings.
Follows clean architecture with dependency injection.
Note: These routes are defined without an extra prefix.
They will be mounted under "/api/cravings" in the main application.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import the repository and DB dependency.
from app.infrastructure.database.repository import CravingRepository, get_db

router = APIRouter()  # Do not include '/cravings' here!

# Pydantic model for updating a craving.
class CravingUpdate(BaseModel):
    description: str | None = None
    intensity: int | None = None
    # Add additional fields as needed.

@router.put("/{craving_id}", tags=["Cravings"])
async def update_craving(craving_id: int, craving_update: CravingUpdate, db: Session = Depends(get_db)):
    """
    Update an existing craving.

    Workflow:
      1. Retrieve the existing craving.
      2. If not found, raise a 404 error.
      3. Otherwise, update only the provided fields.
      4. Return the updated craving.
    """
    repository = CravingRepository(db)
    existing = repository.get_craving_by_id(craving_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Craving not found")
    updated = repository.update_craving(craving_id, craving_update.dict(exclude_unset=True))
    return updated

@router.delete("/{craving_id}", tags=["Cravings"])
async def delete_craving(craving_id: int, db: Session = Depends(get_db)):
    """
    Soft-delete an existing craving.

    Workflow:
      1. Retrieve the craving.
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