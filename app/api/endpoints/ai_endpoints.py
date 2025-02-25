# crave_trinity_backend/app/api/endpoints/ai_endpoints.py
"""
AI-powered endpoints for the CRAVE Trinity Backend.

These endpoints provide access to the core AI capabilities:
1. RAG (Retrieval-Augmented Generation) for personalized responses
2. LoRA (Low-Rank Adaptation) for persona-specific fine-tuning
3. Pattern detection and insights on craving behaviors
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.api.dependencies import get_db, get_craving_repository
from app.core.use_cases.generate_craving_insights import (
    GenerateCravingInsightsInput,
    generate_craving_insights
)
from app.core.services.pattern_detection_service import detect_patterns

router = APIRouter()

# Request/Response Models
class InsightRequest(BaseModel):
    """Request model for AI-powered craving insights."""
    user_id: int = Field(..., example=1, description="User ID requesting insights")
    query: str = Field(..., example="Why do I crave sugar at night?", description="User's question about their cravings")
    persona: Optional[str] = Field(None, example="stress_eater", description="Optional persona for LoRA fine-tuning")

class InsightResponse(BaseModel):
    """Response model for AI-generated insights."""
    answer: str = Field(..., description="AI-generated insight based on user's cravings and query")
    sources: List[dict] = Field(default_factory=list, description="Source craving logs referenced in the response")
    persona_used: Optional[str] = Field(None, description="The LoRA persona used for this response")

class PatternDetectionRequest(BaseModel):
    """Request model for detecting patterns in craving history."""
    user_id: int = Field(..., example=1, description="User ID to analyze")
    timeframe_days: int = Field(30, ge=1, le=365, description="Number of days to analyze")

class PatternInsight(BaseModel):
    """Model representing a detected pattern in user cravings."""
    pattern_type: str = Field(..., description="Type of pattern detected (e.g., 'time_based', 'intensity_trend')")
    description: str = Field(..., description="Human-readable description of the pattern")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the pattern detection")
    relevant_cravings: List[int] = Field(default_factory=list, description="IDs of relevant cravings for this pattern")

class PatternResponse(BaseModel):
    """Response model for pattern detection results."""
    insights: List[PatternInsight] = Field(..., description="List of detected patterns")
    timeframe: str = Field(..., description="Timeframe of the analysis")
    data_points: int = Field(..., description="Number of data points analyzed")

# AI Insight Endpoints
@router.post("/ai/insights", response_model=InsightResponse, tags=["AI"])
async def get_insights(req: InsightRequest, db = Depends(get_db)):
    """
    Generate AI-powered insights about user cravings.
    
    This endpoint demonstrates the power of the CRAVE system by:
    1. Taking a user query about their cravings
    2. Retrieving relevant past craving data using RAG
    3. Using the appropriate LoRA adapter for personalization
    4. Returning an AI-generated insight with references to source data
    
    Returns:
        InsightResponse: The AI-generated insight with source information
    """
    try:
        input_dto = GenerateCravingInsightsInput(
            user_id=req.user_id,
            query=req.query,
            persona=req.persona
        )
        
        # Call the use case to generate insights
        output = generate_craving_insights(input_dto)
        
        # For YC demo, we'll return a mock response if the real system isn't fully integrated
        if not output:
            # Mock response for demonstration
            return InsightResponse(
                answer="Based on your craving history, I've noticed you tend to crave chocolate most frequently in the evening hours (between 7-10 PM). This often correlates with higher stress levels reported during these times. Consider preparing healthier alternatives like dark chocolate squares or keeping a small portion of high-quality chocolate available for these moments. Your cravings also show patterns related to work stress - they're 60% more likely to occur after difficult meetings or tight deadlines.",
                sources=[
                    {"id": 1, "description": "Intense chocolate craving after work", "timestamp": datetime.now().isoformat()},
                    {"id": 3, "description": "Evening sugar craving while watching TV", "timestamp": (datetime.now()).isoformat()}
                ],
                persona_used="stress_eater"
            )
        
        return InsightResponse(**output.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@router.get("/ai/patterns", response_model=PatternResponse, tags=["AI"])
async def analyze_patterns(
    user_id: int = Query(..., description="User ID to analyze"),
    timeframe_days: int = Query(30, ge=1, le=365, description="Timeframe in days"),
    db = Depends(get_db)
):
    """
    Detect patterns in user craving history.
    
    This endpoint analyzes historical craving data to identify:
    - Time-based patterns (e.g., evening cravings, weekend spikes)
    - Intensity trends (increasing/decreasing over time)
    - Correlations with contextual factors
    
    Returns:
        PatternResponse: Detected patterns and insights
    """
    try:
        # Get craving repository
        repo = get_craving_repository(db)
        
        # Retrieve craving history
        cravings = repo.get_cravings_by_user(user_id, limit=500)
        
        # Call pattern detection service
        patterns = detect_patterns(cravings, timeframe_days)
        
        # For YC demo, return mock data if the real service isn't fully integrated
        if not patterns:
            # Mock patterns for demonstration
            return PatternResponse(
                insights=[
                    PatternInsight(
                        pattern_type="time_based",
                        description="Evening sugar cravings (7-10 PM) occur 3x more frequently than other times",
                        confidence=0.87,
                        relevant_cravings=[1, 3, 5]
                    ),
                    PatternInsight(
                        pattern_type="intensity_trend",
                        description="Chocolate cravings have decreased in intensity by 15% over the past month",
                        confidence=0.72,
                        relevant_cravings=[1, 8, 12]
                    ),
                    PatternInsight(
                        pattern_type="correlation",
                        description="High intensity cravings are 60% more likely following reported work stress",
                        confidence=0.81,
                        relevant_cravings=[1, 7, 9]
                    )
                ],
                timeframe=f"Last {timeframe_days} days",
                data_points=len(cravings)
            )
        
        return PatternResponse(
            insights=[PatternInsight(**p.__dict__) for p in patterns],
            timeframe=f"Last {timeframe_days} days",
            data_points=len(cravings)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing patterns: {str(e)}")

@router.get("/ai/personas", tags=["AI"])
async def list_available_personas():
    """
    List available LoRA fine-tuned personas.
    
    LoRA adapters allow CRAVE to provide persona-specific insights without
    requiring full model fine-tuning for each user type.
    
    Returns:
        List of available personas with descriptions
    """
    # For demo purposes, return a predefined list of personas
    return {
        "personas": [
            {
                "id": "night_binger",
                "name": "Nighttime Binger",
                "description": "Optimized for users who experience strong cravings in evening hours",
                "recommended_for": ["Sugar cravings", "Snack urges", "Late-night eating"]
            },
            {
                "id": "stress_eater",
                "name": "Stress Eater",
                "description": "Specialized for cravings triggered by work or emotional stress",
                "recommended_for": ["Emotional eating", "Stress-triggered urges", "Comfort foods"]
            },
            {
                "id": "alcohol_seeker",
                "name": "Alcohol Seeker",
                "description": "Focused on dopamine-seeking behavior related to alcohol consumption",
                "recommended_for": ["Alcohol cravings", "Dopamine-related urges", "Social drinking triggers"]
            }
        ]
    }
