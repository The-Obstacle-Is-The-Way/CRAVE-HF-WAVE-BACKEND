# crave_trinity_backend/app/api/endpoints/ai_endpoints.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.use_cases.generate_craving_insights import (
    GenerateCravingInsightsInput,
    generate_craving_insights
)

router = APIRouter()

class InsightRequest(BaseModel):
    user_id: int
    query: str
    persona: str = None

class InsightResponse(BaseModel):
    answer: str

@router.post("/ai/insights", response_model=InsightResponse)
def get_insights(req: InsightRequest):
    input_dto = GenerateCravingInsightsInput(
        user_id=req.user_id,
        query=req.query,
        persona=req.persona
    )
    output = generate_craving_insights(input_dto)
    return InsightResponse(answer=output.answer)
