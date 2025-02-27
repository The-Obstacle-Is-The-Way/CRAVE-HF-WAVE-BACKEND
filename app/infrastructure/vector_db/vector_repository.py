# File: app/infrastructure/vector_db/vector_repository.py
"""
Vector repository for handling Pinecone-based retrieval operations.
Optimized for fast, reliable search of craving embeddings with comprehensive
error handling and connection management.
"""

import time
import logging
from typing import List, Dict, Any, Optional
import json

from app.config.settings import Settings
from app.infrastructure.vector_db.pinecone_client import get_pinecone_index

# Setup logging
logger = logging.getLogger(__name__)

# Get settings
settings = Settings()

class VectorRepository:
    """
    Repository for vector-based storage and retrieval of craving embeddings.
    
    This class handles all interactions with the vector database (Pinecone),
    providing a clean interface for the rest of the application.
    """
    
    def __init__(self, index_name: Optional[str] = None):
        """
        Initialize the repository with an optional index name override.
        
        Args:
            index_name: Optional override for the Pinecone index name.
                       Defaults to the value from settings.
        """
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        self._index = None
        self._max_retries = 3
        self._retry_delay = 1  # seconds
    
    @property
    def index(self):
        """
        Lazy-loaded Pinecone index property.
        
        Returns:
            The Pinecone index instance, initialized on first use.
        """
        if self._index is None:
            self._index = get_pinecone_index(self.index_name)
        return self._index
    
    def search_cravings(self, embedding: List[float], top_k: int = 10) -> Dict[str, Any]:
        """
        Execute a vector search on Pinecone with retries.
        
        Args:
            embedding: The vector representation of the query
            top_k: The number of top results to retrieve
            
        Returns:
            dict: Search results including metadata
            
        Raises:
            Exception: If all retries fail
        """
        retries = 0
        last_error = None
        
        while retries < self._max_retries:
            try:
                # Execute the query
                results = self.index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                # Log a subtle warning if no matches found
                if len(results.get('matches', [])) == 0:
                    logger.warning(f"Vector search returned no results for query (top_k={top_k})")
                    
                return results
            
            except Exception as e:
                retries += 1
                last_error = e
                logger.warning(
                    f"Vector search failed (attempt {retries}/{self._max_retries}): {str(e)}"
                )
                
                if retries < self._max_retries:
                    # Exponential backoff
                    time.sleep(self._retry_delay * (2 ** (retries - 1)))
        
        # If we get here, all retries failed
        logger.error(f"Vector search failed after {self._max_retries} attempts: {str(last_error)}")
        # Return an empty result structure instead of raising exception
        return {"matches": []}
    
    def upsert_craving_embedding(
        self, 
        craving_id: int, 
        embedding: List[float], 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Upsert a craving's embedding to the Pinecone index with retries.
        
        Args:
            craving_id: Unique identifier of the craving
            embedding: The embedding vector
            metadata: Additional metadata to store
            
        Returns:
            bool: True if the operation succeeded, False otherwise
        """
        retries = 0
        while retries < self._max_retries:
            try:
                # Prepare the vector object
                vector = {
                    "id": str(craving_id),
                    "values": embedding,
                    "metadata": metadata
                }
                
                # Execute the upsert
                self.index.upsert(vectors=[vector])
                
                logger.debug(f"Successfully upserted vector for craving_id={craving_id}")
                return True
                
            except Exception as e:
                retries += 1
                logger.warning(
                    f"Vector upsert failed (attempt {retries}/{self._max_retries}): {str(e)}"
                )
                
                if retries < self._max_retries:
                    # Exponential backoff
                    time.sleep(self._retry_delay * (2 ** (retries - 1)))
        
        # If we get here, all retries failed
        logger.error(
            f"Vector upsert failed after {self._max_retries} attempts for craving_id={craving_id}"
        )
        return False
    
    def delete_craving_embedding(self, craving_id: int) -> bool:
        """
        Delete a craving's embedding from the Pinecone index.
        
        Args:
            craving_id: The ID of the craving to delete
            
        Returns:
            bool: True if the operation succeeded, False otherwise
        """
        try:
            self.index.delete(ids=[str(craving_id)])
            logger.debug(f"Successfully deleted vector for craving_id={craving_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vector for craving_id={craving_id}: {str(e)}")
            return False
    
    def batch_upsert_embeddings(
        self, 
        items: List[Dict[str, Any]]
    ) -> int:
        """
        Upsert multiple craving embeddings in a batch operation.
        
        Args:
            items: List of dicts with 'id', 'embedding', and 'metadata' keys
            
        Returns:
            int: Number of successfully upserted items
        """
        if not items:
            return 0
            
        try:
            # Format vectors for Pinecone batch upsert
            vectors = []
            for item in items:
                vectors.append({
                    "id": str(item['id']),
                    "values": item['embedding'],
                    "metadata": item['metadata']
                })
                
            # Batch upsert to Pinecone
            self.index.upsert(vectors=vectors)
            
            logger.info(f"Successfully batch upserted {len(vectors)} vectors")
            return len(vectors)
            
        except Exception as e:
            logger.error(f"Batch upsert failed: {str(e)}")
            return 0
    
    def get_namespace_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector index.
        
        Returns:
            dict: Statistics including vector count
        """
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {"error": str(e)}

# Create a singleton instance for application-wide use
vector_repository = VectorRepository()