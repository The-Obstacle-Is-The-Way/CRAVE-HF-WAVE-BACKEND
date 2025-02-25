"""
app/api/endpoints/search_cravings.py
--------------------------------------
This endpoint provides vector‑based search functionality for cravings.

Workflow:
  1. It accepts query parameters: user_id, query (text), and an optional top_k.
  2. It constructs a SearchCravingsInput DTO and calls the use case (search_cravings).
  3. The use case generates an embedding for the query text, queries Pinecone for matches,
     and returns a list of CravingSearchResult objects.
  4. The endpoint converts these results to Pydantic models and returns a structured response.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the use case for vector search.
from app.core.use_cases.search_cravings import (
    SearchCravingsInput,
    CravingSearchResult,
    search_cravings
)

# Pydantic model for an individual search result.
class CravingSearchResultOut(BaseModel):
    craving_id: int = Field(..., description="Unique identifier for the craving")
    score: float = Field(..., description="Similarity score from vector search")
    metadata: dict = Field(..., description="Additional metadata (e.g., description, timestamp)")

# Pydantic model for the overall search response.
class SearchResponse(BaseModel):
    results: List[CravingSearchResultOut] = Field(..., description="List of search results")
    count: int = Field(..., description="Total number of results returned")

# Initialize the router.
router = APIRouter()

@router.get("/search", response_model=SearchResponse, tags=["Cravings"])
def search_cravings_endpoint(
    user_id: int = Query(..., description="User ID for search context"),
    query: str = Query(..., description="Search query text"),
    top_k: Optional[int] = Query(5, description="Number of top results to return")
):
    """
    Search for cravings using vector-based methods.
    
    This endpoint:
      1. Builds a SearchCravingsInput DTO using the provided parameters.
      2. Calls the search_cravings use case which:
         - Generates an embedding for the query.
         - Queries Pinecone via VectorRepository for the top matching cravings.
      3. Converts the resulting CravingSearchResult objects into a list of Pydantic models.
      4. Returns a SearchResponse with the list and the total count.
    
    Raises:
      HTTPException 500: If an error occurs during the search process.
    """
    try:
        input_dto = SearchCravingsInput(
            user_id=user_id,
            query_text=query,
            top_k=top_k
        )
        # Call the use case to perform vector search.
        results: List[CravingSearchResult] = search_cravings(input_dto)
        
        # Convert each result to a Pydantic model.
        results_out = [
            CravingSearchResultOut(
                craving_id=result.craving_id,
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
        return SearchResponse(results=results_out, count=len(results_out))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cravings: {str(e)}")