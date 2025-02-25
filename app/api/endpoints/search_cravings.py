"""
app/api/endpoints/search_cravings.py
--------------------------------------
This module implements the search endpoint for the CRAVE Trinity Backend.

It exposes a GET route at /api/cravings/search which:
  • Accepts a query parameter.
  • Uses the CravingRepository to search for matching cravings.
  • Converts the ORM objects into Pydantic models for a consistent response.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List
from app.api.dependencies import get_db, get_craving_repository

# Define a Pydantic model for outputting a craving record.
class CravingOut(BaseModel):
    id: int = Field(..., description="Unique identifier for the craving")
    user_id: int = Field(..., description="User ID associated with the craving")
    description: str = Field(..., description="Text description of the craving")
    intensity: int = Field(..., description="Intensity rating of the craving")
    created_at: str = Field(..., description="Timestamp when the craving was logged")

    class Config:
        from_attributes = True  # Pydantic v2: enable conversion from ORM objects

# Define the response model for a search request.
class SearchResponse(BaseModel):
    cravings: List[CravingOut] = Field(..., description="List of cravings matching the search query")
    count: int = Field(..., description="Total number of matching cravings")

# Initialize the router.
router = APIRouter()

@router.get("/search", response_model=SearchResponse, tags=["Cravings"])
def search_cravings_endpoint(
    query: str = Query(..., description="Search query text"),
    db = Depends(get_db)
):
    """
    Search for cravings that contain the provided query text in their description.
    
    This endpoint:
      1. Retrieves the CravingRepository instance using dependency injection.
      2. Calls the repository's search_cravings method to find matching records.
      3. Converts the ORM objects into Pydantic models using from_orm.
      4. Returns the results along with a count.
    
    Raises:
      HTTPException 500: If an error occurs during processing.
    """
    try:
        # Obtain the repository instance.
        repo = get_craving_repository(db)
        
        # Execute the search; ensure the repository implements search_cravings.
        results = repo.search_cravings(query)
        
        # Convert ORM models to Pydantic models.
        cravings_out = [CravingOut.from_orm(craving) for craving in results]
        return SearchResponse(cravings=cravings_out, count=len(cravings_out))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cravings: {str(e)}")