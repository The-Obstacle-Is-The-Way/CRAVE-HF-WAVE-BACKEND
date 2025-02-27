# File: app/core/use_cases/generate_craving_insights.py

"""
Business logic for generating AI insights from a user's craving history.

We now rely on an injected 'ICravingInsightGenerator' so we can pick
RAG-based generation or any other approach without rewriting the code.
"""

from typing import Optional
from app.core.use_cases.interfaces.icraving_insight_generator import ICravingInsightGenerator
from app.core.use_cases.rag_craving_insight_generator import RagCravingInsightGenerator


def generate_insights(
    user_id: int,
    query: Optional[str] = None,
    insight_generator: ICravingInsightGenerator = None
) -> str:
    """
    Generate analytical insights for a user based on their cravings,
    optionally focused on a query. By default, uses the RagCravingInsightGenerator.
    """

    # Fallback to the RAG-based generator if none is provided
    if insight_generator is None:
        insight_generator = RagCravingInsightGenerator()

    # Delegate to the chosen generator
    return insight_generator.generate_insights(user_id, query)
