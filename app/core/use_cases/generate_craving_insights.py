# crave_trinity_backend/app/core/use_cases/generate_craving_insights.py

from dataclasses import dataclass
from app.core.services.rag_service import generate_personalized_insight

@dataclass
class GenerateCravingInsightsInput:
    user_id: int
    query: str
    persona: str = None

@dataclass
class GenerateCravingInsightsOutput:
    answer: str

def generate_craving_insights(
    input_dto: GenerateCravingInsightsInput
) -> GenerateCravingInsightsOutput:
    response_text = generate_personalized_insight(
        user_id=input_dto.user_id,
        query=input_dto.query,
        persona=input_dto.persona,
        top_k=3
    )
    return GenerateCravingInsightsOutput(answer=response_text)
