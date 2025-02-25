"""
File: crave_trinity-backend/app/api/endpoints/craving_logs.py
Description: This module defines the API endpoints for handling cravings, including creation, listing,
retrieval by ID, and semantic search functionalities. It follows clean code practices and integrates with
the repository and use-case layers for data processing.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

# Import dependencies and use cases
from app.api.dependencies import get_db
from app.core.use_cases.ingest_craving import IngestCravingInput, ingest_craving
from app.core.use_cases.search_cravings import SearchCravingsInput, search_cravings
from app.infrastructure.database.repository import CravingRepository

router = APIRouter()

# =============================================================================
# Request/Response Models
# =============================================================================

class CreateCravingRequest(BaseModel):
    """
    Request model for creating a new craving entry.
    """
    user_id: int = Field(..., example=1, description="The user ID logging the craving")
    description: str = Field(..., example="Sudden urge for chocolate", description="Description of the craving")
    intensity: int = Field(..., ge=1, le=10, example=7, description="Intensity on a scale of 1-10")
    
    @validator('intensity')
    def validate_intensity(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Intensity must be between 1 and 10')
        return v

class CravingResponse(BaseModel):
    """
    Response model for individual craving data.
    """
    id: int = Field(..., description="The unique identifier of the craving")
    user_id: int = Field(..., description="The user who logged the craving")
    description: str = Field(..., description="Description of the craving")
    intensity: int = Field(..., description="Intensity of the craving")
    created_at: datetime = Field(..., description="Timestamp when the craving was created")
    
class CravingListResponse(BaseModel):
    """
    Response model for a list of cravings.
    """
    cravings: List[CravingResponse]
    count: int = Field(..., description="Total number of cravings")

class SearchResult(BaseModel):
    """
    Model for a single search result.
    """
    id: int
    description: str
    intensity: int
    created_at: datetime
    similarity: float = Field(..., description="Similarity score to the query")

class SearchResponse(BaseModel):
    """
    Response model for search results.
    """
    results: List[SearchResult]
    query: str
    count: int

# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/cravings", response_model=CravingResponse, tags=["Cravings"])
async def create_craving(request: CreateCravingRequest, db: Session = Depends(get_db)):
    """
    Create a new craving entry.
    
    Logs a user's craving (description and intensity) to the database.
    
    Returns:
        CravingResponse: The created craving, including its ID and timestamp.
    """
    try:
        repo = CravingRepository(db)
        input_dto = IngestCravingInput(
            user_id=request.user_id,
            description=request.description,
            intensity=request.intensity
        )
        output = ingest_craving(input_dto, repo)
        return CravingResponse(**output.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create craving: {str(e)}")

@router.get("/cravings", response_model=CravingListResponse, tags=["Cravings"])
async def list_cravings(
    user_id: int = Query(..., description="User ID to filter cravings"),
    skip: int = Query(0, ge=0, description="Number of cravings to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of cravings to return"),
    db: Session = Depends(get_db)
):
    """
    List cravings for a specific user with pagination.
    
    Retrieves a paginated list of cravings for the provided user ID.
    
    Returns:
        CravingListResponse: A list of cravings along with the total count.
    """
    try:
        repo = CravingRepository(db)
        cravings = repo.get_cravings_by_user(user_id, skip, limit)
        count = repo.count_cravings_by_user(user_id)
        return CravingListResponse(
            cravings=[CravingResponse(**c.__dict__) for c in cravings],
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cravings: {str(e)}")

@router.get("/cravings/{craving_id}", response_model=CravingResponse, tags=["Cravings"])
async def get_craving(
    craving_id: int = Path(..., description="ID of the craving to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific craving by its ID.
    
    Returns detailed information about a single craving.
    
    Returns:
        CravingResponse: The craving details.
    """
    try:
        repo = CravingRepository(db)
        craving = repo.get_craving(craving_id)
        if not craving:
            raise HTTPException(status_code=404, detail=f"Craving with ID {craving_id} not found")
        return CravingResponse(**craving.__dict__)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve craving: {str(e)}")

@router.get("/cravings/search", response_model=SearchResponse, tags=["Cravings"])
async def search_cravings_endpoint(
    user_id: int = Query(..., description="User ID to search cravings for"),
    query_text: str = Query(..., description="Text to search for in cravings"),
    top_k: int = Query(5, ge=1, le=100, description="Number of results to return")
):
    """
    Search for cravings using semantic similarity.
    
    Leverages vector embeddings to find cravings similar to the provided query text.
    This powers the RAG (Retrieval-Augmented Generation) component of the system.
    
    Returns:
        SearchResponse: A list of similar cravings with their similarity scores.
    """
    try:
        input_dto = SearchCravingsInput(
            user_id=user_id,
            query_text=query_text,
            top_k=top_k
        )
        results = search_cravings(input_dto)
        return SearchResponse(
            results=[SearchResult(**r.__dict__) for r in results],
            query=query_text,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
