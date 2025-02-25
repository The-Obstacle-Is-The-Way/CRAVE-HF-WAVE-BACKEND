"""
User Queries Endpoints for CRAVE Trinity.

This endpoint module handles incoming user queries,
delegating database operations to the CravingRepository.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db  # Assumes a dependency that returns a SQLAlchemy Session
from app.infrastructure.database.repository import CravingRepository
from app.core.entities.craving import Craving  # Pydantic model for response serialization

router = APIRouter()

@router.get("/cravings", response_model=dict)
def read_cravings(
    user_id: int = Query(..., description="ID of the user to retrieve cravings for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all cravings logged by a specific user.

    :param user_id: The ID of the user.
    :param db: SQLAlchemy Session provided via dependency injection.
    :return: A dictionary with a list of cravings and their total count.
    """
    repository = CravingRepository(db)
    cravings = repository.get_cravings_by_user(user_id)
    
    # If no cravings are found, return an empty list with a count of 0.
    if not cravings:
        return {"cravings": [], "count": 0}
    
    # Serialize each SQLAlchemy model to a dict using the Pydantic model.
    cravings_data = [Craving.from_orm(craving).dict() for craving in cravings]
    return {"cravings": cravings_data, "count": len(cravings_data)}