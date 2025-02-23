# crave_trinity_backend/app/infrastructure/vector_db/vector_repository.py

from typing import List
import pinecone
from app.infrastructure.vector_db.pinecone_client import get_pinecone_index
from app.config.settings import Settings

# Load settings from environment
settings = Settings()

class VectorRepository:
    def __init__(self, index_name: str = None):
        """
        Initializes the vector repository.
        
        Parameters:
          index_name (str): The name of the Pinecone index to use.
                            Defaults to the one specified in Settings.
        """
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        # Retrieve the Pinecone index (this will also initialize Pinecone)
        self.index = get_pinecone_index(self.index_name)

    def upsert_craving_embedding(
        self, 
        craving_id: int, 
        embedding: List[float], 
        metadata: dict
    ) -> None:
        """
        Upserts a craving vector into the Pinecone index.
        
        Parameters:
          craving_id (int): Unique identifier for the craving record.
          embedding (List[float]): The embedding vector.
          metadata (dict): Additional metadata to store with the vector.
        """
        upsert_data = [(str(craving_id), embedding, metadata)]
        self.index.upsert(vectors=upsert_data)

    def query_cravings(
        self, 
        query_embedding: List[float], 
        top_k: int = 5
    ) -> List[dict]:
        """
        Queries the Pinecone index for vectors similar to the query vector.
        
        Parameters:
          query_embedding (List[float]): The embedding vector for the query.
          top_k (int): The number of nearest neighbors to return.
        
        Returns:
          A list of dictionaries containing 'id', 'score', and 'metadata' for each match.
        """
        result = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_values=False,  # We don't need the stored vector in the response
            include_metadata=True
        )
        matches = []
        for match in result.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        return matches
