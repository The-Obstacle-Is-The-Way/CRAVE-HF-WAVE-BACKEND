# File: app/api/endpoints/user_queries.py
"""
Endpoints for updating and deleting cravings.
Follows clean architecture with dependency injection.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.infrastructure.database.repository import CravingRepository, get_db
from sqlalchemy.orm import Session

router = APIRouter()

class CravingUpdate(BaseModel):
    description: str | None = None
    intensity: int | None = None
    # Add additional fields as needed

@router.put("/api/cravings/{craving_id}", tags=["Cravings"])
async def update_craving(craving_id: int, craving_update: CravingUpdate, db: Session = Depends(get_db)):
    repository = CravingRepository(db)
    existing = repository.get_craving_by_id(craving_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Craving not found")
    updated = repository.update_craving(craving_id, craving_update.dict(exclude_unset=True))
    return updated

@router.delete("/api/cravings/{craving_id}", tags=["Cravings"])
async def delete_craving(craving_id: int, db: Session = Depends(get_db)):
    repository = CravingRepository(db)
    existing = repository.get_craving_by_id(craving_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Craving not found")
    repository.delete_craving(craving_id)
    return {"detail": "Craving deleted successfully"}