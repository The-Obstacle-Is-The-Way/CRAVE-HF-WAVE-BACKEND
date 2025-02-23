# crave_trinity_backend/app/core/use_cases/ingest_craving.py

from dataclasses import dataclass
from typing import Optional

from app.core.entities.craving import Craving
from app.infrastructure.database.repository import CravingRepository
from datetime import datetime

@dataclass
class IngestCravingInput:
    user_id: int
    description: str
    intensity: int

@dataclass
class IngestCravingOutput:
    id: int
    user_id: int
    description: str
    intensity: int
    created_at: datetime

def ingest_craving(input_dto: IngestCravingInput, repo: CravingRepository) -> IngestCravingOutput:
    """
    Ingest a new craving into the system.
    """
    domain_craving = Craving(
        id=None,
        user_id=input_dto.user_id,
        description=input_dto.description,
        intensity=input_dto.intensity,
        created_at=datetime.utcnow(),  # or the server default
    )

    saved_craving = repo.create_craving(domain_craving)

    return IngestCravingOutput(
        id=saved_craving.id,
        user_id=saved_craving.user_id,
        description=saved_craving.description,
        intensity=saved_craving.intensity,
        created_at=saved_craving.created_at,
    )

# ingest_craving.py
from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService
from app.infrastructure.vector_db.vector_repository import VectorRepository

...

def ingest_craving(input_dto: IngestCravingInput, repo: CravingRepository) -> IngestCravingOutput:
    ...
    saved_craving = repo.create_craving(domain_craving)

    # Now optionally embed + store in Pinecone
    try:
        embed_service = OpenAIEmbeddingService()
        embedding = embed_service.embed_text(saved_craving.description)

        # You can store user_id, created_at, etc. in metadata
        vector_repo = VectorRepository()
        metadata = {"user_id": saved_craving.user_id, "created_at": str(saved_craving.created_at)}
        vector_repo.upsert_craving_embedding(saved_craving.id, embedding, metadata)
    except Exception as e:
        # Log it, or handle gracefully
        pass

    return IngestCravingOutput(...)
