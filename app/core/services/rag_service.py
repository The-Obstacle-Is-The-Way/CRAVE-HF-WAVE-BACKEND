# File: app/core/services/rag_service.py
"""
Retrieval-Augmented Generation (RAG) Service for CRAVE Trinity Backend.

This service implements a robust RAG pipeline that:
1. Creates embeddings for user queries
2. Retrieves relevant context from vector database
3. Constructs optimized prompts with time-weighted retrieval
4. Generates personalized responses using either base or LoRA-adapted LLMs
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from app.core.services.embedding_service import embedding_service
from app.infrastructure.vector_db.vector_repository import VectorRepository
from app.infrastructure.llm.lora_adapter import LoRAAdapterManager
from app.infrastructure.llm.llama2_adapter import Llama2Adapter
from app.config.settings import Settings

settings = Settings()
logger = logging.getLogger(__name__)

@dataclass
class RetrievedCraving:
    """Represents a retrieved craving from the vector database."""
    id: int
    description: str
    created_at: datetime
    intensity: int
    score: float  # Similarity score from vector search
    time_score: float = 1.0  # Time-weighted adjustment (1.0 = no adjustment)
    
    @property
    def final_score(self) -> float:
        """Calculate the final score with time weighting applied."""
        return self.score * self.time_score

class RAGService:
    """
    Implements the Retrieval-Augmented Generation pipeline.
    
    This service handles:
    - Query embedding
    - Context retrieval with time weighting
    - Prompt construction
    - LLM generation with persona customization
    """
    
    def __init__(self):
        """Initialize the RAG service with dependencies."""
        self.vector_repo = VectorRepository()
        
    def generate_personalized_insight(
        self, 
        user_id: int, 
        query: str, 
        persona: Optional[str] = None,
        top_k: int = 5,
        time_weighted: bool = True,
        recency_boost_days: int = 30
    ) -> str:
        """
        Generate a personalized craving insight for the user's query.
        
        Args:
            user_id: The user's ID
            query: The user's question or query text
            persona: Optional LoRA persona to use (NighttimeBinger, StressCraver, etc.)
            top_k: Number of relevant cravings to retrieve
            time_weighted: Whether to apply time-weighted retrieval
            recency_boost_days: Days for which to apply maximum recency boost
            
        Returns:
            A personalized response based on the user's cravings history
        """
        try:
            # 1. Embed the query
            query_embedding = embedding_service.get_embedding(query)
            
            # 2. Retrieve relevant cravings with vector search
            search_results = self.vector_repo.search_cravings(
                embedding=query_embedding, 
                top_k=top_k * 2  # Retrieve more than needed for time-weighted filtering
            )
            
            # 3. Process search results into domain objects
            retrieved_cravings = self._process_search_results(search_results)
            
            # 4. Apply time-weighted scoring if enabled
            if time_weighted and retrieved_cravings:
                retrieved_cravings = self._apply_time_weighting(
                    retrieved_cravings, 
                    recency_boost_days=recency_boost_days
                )
                
            # 5. Truncate to the actual top_k after time weighting
            retrieved_cravings = retrieved_cravings[:top_k]
            
            # 6. Construct prompt with retrieved context
            prompt = self._construct_prompt(user_id, query, retrieved_cravings)
            
            # 7. Generate response with appropriate model
            if persona and persona in settings.LORA_PERSONAS:
                logger.info(f"Using LoRA persona '{persona}' for generation")
                adapter_path = settings.LORA_PERSONAS[persona]
                answer = LoRAAdapterManager.generate_text_with_adapter(adapter_path, prompt)
            else:
                logger.info("Using base model for generation")
                answer = Llama2Adapter.generate_text(prompt)
                
            return answer
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}", exc_info=True)
            # Provide a graceful fallback response
            return (
                "I'm having trouble accessing your craving history right now. "
                "Please try again in a moment or rephrase your question."
            )
    
    def _process_search_results(self, search_results: Dict[str, Any]) -> List[RetrievedCraving]:
        """
        Process raw vector search results into domain objects.
        
        Args:
            search_results: Raw search results from Pinecone
            
        Returns:
            List of RetrievedCraving objects
        """
        retrieved_cravings = []
        
        for match in search_results.get("matches", []):
            try:
                # Extract metadata from the match
                metadata = match.get("metadata", {})
                created_at_str = metadata.get("created_at", "")
                
                # Parse timestamp
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str)
                else:
                    created_at = datetime.utcnow()  # Fallback
                
                # Extract craving ID from match ID (assuming match id format)
                try:
                    craving_id = int(match.get("id", "0"))
                except ValueError:
                    craving_id = 0
                
                # Create domain object
                craving = RetrievedCraving(
                    id=craving_id,
                    description=metadata.get("description", "Unknown craving"),
                    created_at=created_at,
                    intensity=metadata.get("intensity", 0),
                    score=match.get("score", 0.0)
                )
                retrieved_cravings.append(craving)
                
            except Exception as e:
                logger.warning(f"Error processing search result: {str(e)}")
                continue
                
        return retrieved_cravings
    
    def _apply_time_weighting(
        self, 
        cravings: List[RetrievedCraving], 
        recency_boost_days: int = 30
    ) -> List[RetrievedCraving]:
        """
        Apply time-weighted scoring to retrieved cravings.
        
        Args:
            cravings: List of retrieved cravings
            recency_boost_days: Days for which to apply maximum recency boost
            
        Returns:
            Time-weighted and re-sorted cravings
        """
        now = datetime.utcnow()
        recency_threshold = timedelta(days=recency_boost_days)
        
        for craving in cravings:
            age = now - craving.created_at
            
            if age <= recency_threshold:
                # Maximum boost for recent cravings
                craving.time_score = 1.0
            else:
                # Progressive decay for older cravings
                days_old = age.total_seconds() / 86400  # Convert to days
                # Exponential decay formula, never goes below 0.2
                craving.time_score = max(0.2, 1.0 * (0.95 ** (days_old - recency_boost_days)))
        
        # Re-sort by final_score and return
        return sorted(cravings, key=lambda c: c.final_score, reverse=True)
    
    def _construct_prompt(
        self, 
        user_id: int, 
        query: str, 
        retrieved_cravings: List[RetrievedCraving]
    ) -> str:
        """
        Construct an optimized prompt for the LLM.
        
        Args:
            user_id: The user's ID
            query: The user's question
            retrieved_cravings: List of relevant cravings for context
            
        Returns:
            A structured prompt for the LLM
        """
        # Build context from retrieved cravings
        if not retrieved_cravings:
            context_text = "No relevant craving data found in your history."
        else:
            context_lines = []
            for i, craving in enumerate(retrieved_cravings, 1):
                # Format date for readability
                date_str = craving.created_at.strftime("%b %d, %Y at %I:%M %p")
                context_lines.append(
                    f"{i}. {craving.description} (Intensity: {craving.intensity}/10, {date_str})"
                )
            context_text = "\n".join(context_lines)

        # Construct a comprehensive prompt with system instructions and context
        prompt = f"""You are CRAVE AI, a specialized assistant designed to help people understand their cravings.

USER PROFILE:
- User ID: {user_id}

RELEVANT CRAVING HISTORY:
{context_text}

USER QUERY:
{query}

GUIDELINES:
1. Provide an empathetic, insightful response based on the user's craving patterns.
2. Ground your response in their actual history, NOT general advice.
3. Identify patterns or triggers if apparent in their data.
4. Be supportive and non-judgmental.
5. Focus on understanding patterns rather than providing medical advice.
6. If you don't have enough data to answer confidently, acknowledge this limitation.

YOUR RESPONSE:
"""
        return prompt

# Singleton instance for application-wide use
rag_service = RAGService()

# Function interface for backwards compatibility
def generate_personalized_insight(
    user_id: int, 
    query: str, 
    persona: str = None, 
    top_k: int = 5
) -> str:
    """Backwards-compatible function interface for the RAG service."""
    return rag_service.generate_personalized_insight(
        user_id=user_id,
        query=query,
        persona=persona,
        top_k=top_k
    )