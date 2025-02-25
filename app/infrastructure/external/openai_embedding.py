# crave_trinity_backend/app/infrastructure/external/openai_embedding.py
"""
OpenAI embedding service to create vector representations of text.
"""
from typing import List
from app.config.settings import Settings
import openai

settings = Settings()

class OpenAIEmbeddingService:
    """Service for creating embeddings using OpenAI's API."""
    
    def __init__(self, api_key=None):
        """Initialize with optional API key override."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using OpenAI's API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Configure OpenAI client
            client = openai.OpenAI(api_key=self.api_key)
            
            # New OpenAI API (>=1.0.0)
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            # Extract embeddings
            return [item.embedding for item in response.data]
        except Exception as e:
            # For demo purposes, return mock embeddings if API fails
            print(f"Warning: OpenAI embedding error: {e}")
            
            # Return mock embeddings (dimensionality matches text-embedding-ada-002)
            import random
            mock_dim = 1536  # text-embedding-ada-002 has 1536 dimensions
            return [[random.random() for _ in range(mock_dim)] for _ in texts]

# For backwards compatibility
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Function wrapper for the service."""
    service = OpenAIEmbeddingService()
    return service.get_embeddings(texts)
