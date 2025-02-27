# app/api/endpoints/user_queries.py
"""
Endpoints for querying and managing user-specific craving data.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict  # Import ConfigDict
from sqlalchemy.orm import Session

from app.infrastructure.database.repository import CravingRepository
from app.api.dependencies import get_db, get_current_user
from app.infrastructure.database.models import UserModel

router = APIRouter()

class Craving(BaseModel):
    """Pydantic model for a craving."""
    id: int
    user_id: int
    description: str
    intensity: int
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)


class CravingsResponse(BaseModel):
    """Response model for a list of cravings."""
    cravings: List[Craving]
    model_config = ConfigDict(from_attributes=True)

@router.get("/user/queries", response_model=CravingsResponse, tags=["Cravings"])
async def get_user_cravings(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CravingsResponse:
    """
    Retrieves all cravings for the currently authenticated user.
    """
    craving_repo = CravingRepository(db)
    db_cravings = craving_repo.get_cravings_for_user(current_user.id)

    cravings = [
        Craving(
            id=c.id,
            user_id=c.user_id,
            description=c.description,
            intensity=c.intensity,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in db_cravings
    ]

    return CravingsResponse(cravings=cravings)

@router.delete("/user/queries/{craving_id}", tags=["Cravings"])
async def delete_user_craving(
    craving_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific craving for the authenticated user. Implements soft delete.
    """
    craving_repo = CravingRepository(db)
    craving = craving_repo.get_craving_by_id(craving_id)

    if not craving:
        raise HTTPException(status_code=404, detail="Craving not found")

    if craving.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this craving")

    craving_repo.delete_craving(craving_id)
    return {"message": f"Craving {craving_id} deleted successfully"}