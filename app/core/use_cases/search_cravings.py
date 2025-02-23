# crave_trinity_backend/app/core/use_cases/search_cravings.py

from dataclasses import dataclass
from typing import List
from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService
from app.infrastructure.vector_db.vector_repository import VectorRepository

@dataclass
class SearchCravingsInput:
    user_id: int
    query_text: str
    top_k: int = 5

@dataclass
class CravingSearchResult:
    craving_id: int
    score: float
    metadata: dict  # Additional info if stored in Pinecone

def search_cravings(input_dto: SearchCravingsInput) -> List[CravingSearchResult]:
    # 1) Get embedding for query text
    embed_service = OpenAIEmbeddingService()
    query_embedding = embed_service.embed_text(input_dto.query_text)

    # 2) Query Pinecone for top_k matches
    vector_repo = VectorRepository()
    matches = vector_repo.query_cravings(query_embedding, top_k=input_dto.top_k)

    # 3) Convert results into domain-friendly objects
    results = [
        CravingSearchResult(
            craving_id=int(match["id"]),
            score=match["score"],
            metadata=match.get("metadata", {})
        )
        for match in matches
    ]
    return results
