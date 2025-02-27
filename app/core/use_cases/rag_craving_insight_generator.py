# File: app/core/use_cases/rag_craving_insight_generator.py

from typing import Optional
import logging
from app.core.use_cases.interfaces.icraving_insight_generator import ICravingInsightGenerator
from app.core.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class RagCravingInsightGenerator(ICravingInsightGenerator):
    """
    Generates craving insights using the RAG pipeline. 
    This class implements the ICravingInsightGenerator interface.
    """

    def generate_insights(self, user_id: int, query: Optional[str] = None) -> str:
        """
        Generate a textual summary of insights using RAG. If no query is provided,
        we can default to a more general 'insights' style prompt.
        """
        # If the user didn’t specify a query, we can craft a generic query
        # or simply return a generic string or the result of a default RAG query.
        rag_query = query or "Summarize this user's craving history in a helpful, concise manner."
        
        # We can choose top_k or any other parameters that make sense in "insight" context
        top_k = 5

        try:
            # Instead of a persona, you could also pass some specialized
            # "InsightPersona" if you have a LoRA model for that. For now, None.
            answer = rag_service.generate_personalized_insight(
                user_id=user_id,
                query=rag_query,
                persona=None,      # or a specific persona if desired
                top_k=top_k,
                time_weighted=True # we can keep time weighting if we want recency
            )
            return answer
        
        except Exception as e:
            logger.error(f"Error generating insights using RAG for user {user_id}: {str(e)}", exc_info=True)
            return (
                "Sorry, I'm having trouble generating RAG-based insights right now. "
                "Please try again in a moment."
            )
