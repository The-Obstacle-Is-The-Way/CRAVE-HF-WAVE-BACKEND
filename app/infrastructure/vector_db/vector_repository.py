# File: app/infrastructure/vector_db/vector_repository.py
"""
Vector repository for handling Pinecone-based retrieval operations.
Optimized for fast, reliable search of craving embeddings.
This file now correctly instantiates the Settings class from app/config/settings.py
to access PINECONE_INDEX_NAME.
"""

import pinecone
from app.config.settings import Settings  # Import the Settings class

# Instantiate the settings to access configuration values.
settings = Settings()

class VectorRepository:
    def __init__(self):
        # Initialize the Pinecone index using the index name from settings.
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)

    def search_cravings(self, embedding: list[float], top_k: int = 10) -> dict:
        """
        Execute a vector search on Pinecone.

        Args:
            embedding (list[float]): The vector representation of the query.
            top_k (int): The number of top results to retrieve.

        Returns:
            dict: Search results including metadata.
        """
        results = self.index.query(vector=embedding, top_k=top_k, include_metadata=True)
        return results

    def upsert_craving_embedding(self, craving_id: int, embedding: list[float], metadata: dict) -> None:
        """
        Upsert a craving's embedding to the Pinecone index.

        Args:
            craving_id (int): Unique identifier of the craving.
            embedding (list[float]): The embedding vector.
            metadata (dict): Additional metadata to store.
        """
        vector = {
            "id": str(craving_id),
            "values": embedding,
            "metadata": metadata
        }
        self.index.upsert(vectors=[vector])