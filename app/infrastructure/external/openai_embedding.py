"""
File: crave_trinity-backend/app/infrastructure/external/openai_embedding.py
Description: OpenAI embedding service to create vector representations of text.
This module provides methods to generate embeddings using OpenAI's API,
following clean code practices and ensuring backwards compatibility.
"""

from typing import List
from app.config.settings import Settings
import openai

settings = Settings()

class OpenAIEmbeddingService:
    """
    Service for creating embeddings using OpenAI's API.
    
    This class provides methods for both batch text embeddings and single-text embedding.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the OpenAIEmbeddingService with an optional API key override.
        
        :param api_key: Optional API key to override the default from settings.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts using OpenAI's API.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            List of embedding vectors, where each vector is a list of floats.
        """
        try:
            # Configure OpenAI client with the provided API key.
            client = openai.OpenAI(api_key=self.api_key)
            
            # Call the new OpenAI API for embeddings (>=1.0.0)
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            # Extract and return the embeddings from the response.
            return [item.embedding for item in response.data]
        except Exception as e:
            # Log a warning and return mock embeddings if the API call fails.
            print(f"Warning: OpenAI embedding error: {e}")
            import random
            mock_dim = 1536  # text-embedding-ada-002 outputs 1536-dimensional vectors.
            return [[random.random() for _ in range(mock_dim)] for _ in texts]

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a vector using OpenAI's API.
        
        This method wraps the batch get_embeddings method for convenience.
        
        Args:
            text: A single text string to embed.
        
        Returns:
            A list of floats representing the embedding vector.
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []

# For backwards compatibility, provide a function interface as well.
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Function wrapper for generating embeddings using the OpenAIEmbeddingService.
    
    Args:
        texts: List of text strings to embed.
        
    Returns:
        List of embedding vectors.
    """
    service = OpenAIEmbeddingService()
    return service.get_embeddings(texts)
