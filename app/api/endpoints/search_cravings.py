"""
app/api/endpoints/search_cravings.py
-------------------------------------
This module implements the search endpoint for the CRAVE Trinity Backend.

It provides a route to search for cravings based on text queries by leveraging
the repository’s search functionality. The endpoint is designed to be robust,
extensible, and production‑ready.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List
from app.api.dependencies import get_db, get_craving_repository

# Define an output model for a craving record.
class CravingOut(BaseModel):
    id: int = Field(..., description="Unique identifier for the craving")
    user_id: int = Field(..., description="User ID associated with the craving")
    description: str = Field(..., description="Text description of the craving")
    intensity: int = Field(..., description="Intensity rating of the craving")
    created_at: str = Field(..., description="Timestamp when the craving was logged")

    class Config:
        orm_mode = True

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
    Search for cravings that match the provided query text.
    
    This endpoint:
      1. Retrieves a CravingRepository instance using dependency injection.
      2. Uses the repository’s search_cravings method to find matching records.
      3. Returns a list of matching cravings and the total count.
      
    Raises:
        HTTPException 500: If any error occurs during the search process.
    """
    try:
        repo = get_craving_repository(db)
        # Call the repository's search method.
        # Note: Ensure that your CravingRepository implements a method named 'search_cravings'.
        results = repo.search_cravings(query)
        return SearchResponse(cravings=results, count=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cravings: {str(e)}")