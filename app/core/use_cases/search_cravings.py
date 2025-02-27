"""
app/core/use_cases/search_cravings.py
-------------------------------------
This module implements the vector-based search for cravings.

It defines the input and output data transfer objects (DTOs) and the
business logic for performing a vector search using OpenAI embeddings
and Pinecone via the VectorRepository.

Note:
  If these DTOs are needed in multiple modules, consider moving them to a
  separate module (e.g., app/core/use_cases/search_cravings_dto.py) to avoid
  circular dependencies.
"""

from dataclasses import dataclass
from typing import List
from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService
from app.infrastructure.vector_db.vector_repository import VectorRepository

@dataclass
class SearchCravingsInput:
    """
    DTO for search cravings use case.
    
    Attributes:
        user_id (int): The user for whom to search cravings.
        query_text (str): The text query to search for.
        top_k (int, optional): Number of top matching results to return (default is 5).
    """
    user_id: int
    query_text: str
    top_k: int = 5

@dataclass
class CravingSearchResult:
    """
    DTO for a single search result.
    
    Attributes:
        craving_id (int): Unique identifier for the craving.
        score (float): Similarity score from vector search.
        metadata (dict): Additional metadata (if any) returned by Pinecone.
    """
    craving_id: int
    score: float
    metadata: dict

def search_cravings(input_dto: SearchCravingsInput) -> List[CravingSearchResult]:
    """
    Executes a vector-based search for cravings.
    
    Workflow:
      1. Generate an embedding for the input query using OpenAIEmbeddingService.
      2. Query the Pinecone index via VectorRepository to retrieve the top matches.
      3. Convert the raw match data into a list of CravingSearchResult instances.
    
    Args:
        input_dto (SearchCravingsInput): Input parameters for the search.
    
    Returns:
        List[CravingSearchResult]: A list of search results.
    """
    # 1. Generate embedding for the query text.
    embed_service = OpenAIEmbeddingService()
    query_embedding = embed_service.embed_text(input_dto.query_text)
    
    # 2. Query Pinecone for the top matching cravings.
    vector_repo = VectorRepository()
    matches = vector_repo.query_cravings(query_embedding, top_k=input_dto.top_k)
    
    # 3. Convert the matches to CravingSearchResult instances.
    results = [
        CravingSearchResult(
            craving_id=int(match["id"]),
            score=match["score"],
            metadata=match.get("metadata", {})
        )
        for match in matches
    ]
    return results