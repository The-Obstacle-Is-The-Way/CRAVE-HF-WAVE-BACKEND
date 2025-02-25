# crave_trinity_backend/app/api/endpoints/ai_endpoints.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.use_cases.generate_craving_insights import (
    GenerateCravingInsightsInput,
    generate_craving_insights
)

router = APIRouter()

class InsightRequest(BaseModel):
    """
    Request model for AI insight generation.
    """
    user_id: int = Field(..., example=1, description="User ID requesting insights")
    query: str = Field(..., example="Why do I crave sugar at night?", description="User's question about their cravings")
    persona: str = Field(None, example="stress_eater", description="Optional persona for LoRA fine-tuning")

class InsightResponse(BaseModel):
    """
    Response model for AI-generated insights.
    """
    answer: str = Field(..., description="AI-generated insight based on user's cravings and query")

@router.post("/ai/insights", response_model=InsightResponse, tags=["AI"])
async def get_insights(req: InsightRequest):
    """
    Generate AI-powered insights about user cravings.
    
    This endpoint:
    1. Takes a user query about their cravings
    2. Retrieves relevant past craving data using RAG
    3. Uses the appropriate LoRA adapter for personalization
    4. Returns an AI-generated insight
    
    Returns:
        InsightResponse: The AI-generated insight
    """
    try:
        input_dto = GenerateCravingInsightsInput(
            user_id=req.user_id,
            query=req.query,
            persona=req.persona
        )
        output = generate_craving_insights(input_dto)
        return InsightResponse(answer=output.answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")
