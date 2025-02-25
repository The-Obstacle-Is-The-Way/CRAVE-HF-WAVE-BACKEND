"""
Directory Structure (flattened):
----------------------------------
/app
 ├── api
 │    ├── main.py           <-- API entry point
 │    ├── dependencies.py
 │    └── endpoints
 │         ├── health.py
 │         ├── user_queries.py   <-- This file
 │         ├── craving_logs.py
 │         ├── ai_endpoints.py
 │         └── search_cravings.py
 ...
/app/core/entities/craving.py   <-- Pydantic model for Craving
/app/infrastructure/database/repository.py   <-- CravingRepository

Description:
This module handles incoming user queries for retrieving cravings.
It delegates data access to the CravingRepository and returns a well‑structured
response using a dedicated Pydantic model.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List

# Dependency: Provides a SQLAlchemy session.
from app.api.dependencies import get_db

# Repository for interacting with the cravings table.
from app.infrastructure.database.repository import CravingRepository

# Domain model for a craving (ensure this model is configured with orm_mode/from_attributes).
from app.core.entities.craving import Craving

# Define a dedicated response model for listing cravings.
class CravingListResponse(BaseModel):
    cravings: List[Craving] = Field(..., description="List of cravings for the user")
    count: int = Field(..., description="Total number of cravings returned")

    class Config:
        # For Pydantic v2, ensure conversion from ORM objects.
        from_attributes = True

router = APIRouter()

@router.get("/cravings", response_model=CravingListResponse, tags=["Cravings"])
def read_cravings(
    user_id: int = Query(..., description="ID of the user to retrieve cravings for"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all cravings logged by a specific user.

    Workflow:
      1. Receive a user_id via query parameters.
      2. Obtain a database session through dependency injection.
      3. Use CravingRepository to fetch the user's cravings.
      4. Convert the ORM objects to Pydantic models using from_orm.
      5. Return a structured response containing the list of cravings and a count.

    Returns:
        CravingListResponse: Contains a list of cravings and the total count.

    Raises:
        HTTPException (500): If an error occurs during database operations.
    """
    try:
        repository = CravingRepository(db)
        cravings = repository.get_cravings_by_user(user_id)
        
        # Return an empty list if no cravings are found.
        if not cravings:
            return CravingListResponse(cravings=[], count=0)
        
        # Convert each SQLAlchemy model instance into a Pydantic model.
        cravings_out = [Craving.from_orm(craving) for craving in cravings]
        return CravingListResponse(cravings=cravings_out, count=len(cravings_out))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cravings: {str(e)}")