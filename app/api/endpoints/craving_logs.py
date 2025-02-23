# File: crave_trinity_backend/app/api/endpoints/craving_logs.py
# This module defines the FastAPI endpoints for handling craving logging.
# Uncle Bob would say: "Keep your layers separated and your business rules pure.
# The API is merely a thin layer that delegates work to the domain use cases."
# Make sure your endpoint is simple, clean, and testable.

from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.use_cases.ingest_craving import IngestCravingInput, ingest_craving
from app.infrastructure.database.repository import CravingRepository

router = APIRouter()

# Request model: Define the structure of data coming into the API.
class CreateCravingRequest(BaseModel):
    user_id: int = Field(..., example=1)            # The ID of the user logging the craving
    description: str = Field(..., example="Sudden urge for chocolate")
    intensity: int = Field(..., example=7)           # Intensity on a scale, for example 1-10

# Response model: Define the structure of data leaving the API.
class CravingResponse(BaseModel):
    id: int                                         # The unique identifier of the craving
    user_id: int                                    # The user who logged the craving
    description: str                                # Description of the craving
    intensity: int                                  # Intensity of the craving
    created_at: datetime                            # Timestamp when the craving was created

@router.post("/cravings", response_model=CravingResponse, tags=["Cravings"])
def create_craving(req: CreateCravingRequest, db: Session = Depends(get_db)):
    """
    Endpoint to create a new craving entry.
    Uncle Bob says: "Let the domain logic handle the business, not the API."
    """
    # Create a repository instance to interact with the database.
    repo = CravingRepository(db)
    # Build the input DTO for the use case.
    input_dto = IngestCravingInput(
        user_id=req.user_id,
        description=req.description,
        intensity=req.intensity
    )
    # Call the use case to perform the business logic of ingesting the craving.
    output = ingest_craving(input_dto, repo)
    # Return the response by unpacking the output object's attributes.
    return CravingResponse(**output.__dict__)
