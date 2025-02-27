# File: app/core/services/embedding_service.py
"""
Embedding Service for CRAVE Trinity Backend.

This service centralizes access to text embedding functionality, 
providing a clean interface between application logic and the 
embedding provider (OpenAI).

It implements:
1. Caching for performance optimization
2. Error handling and fallback strategies
3. Consistent embedding dimensionality
"""

from typing import List, Dict, Optional, Union, Any
import hashlib
import json
from datetime import datetime, timedelta
import logging

from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService

# Setup logging
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    
    This service provides a high-level interface for converting text
    to vector embeddings, with caching and error handling.
    """
    
    def __init__(self):
        """Initialize the embedding service with OpenAI integration and caching."""
        self.openai_service = OpenAIEmbeddingService()
        # In-memory cache for embeddings - in production, consider Redis
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache embeddings for 24 hours
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for a single text string, with caching.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
        cache_key = self._get_cache_key(text)
        cached = self._get_from_cache(cache_key)
        
        if cached:
            logger.debug(f"Cache hit for embedding: {cache_key[:8]}...")
            return cached
            
        # Get embedding from OpenAI
        try:
            embedding = self.openai_service.embed_text(text)
            self._add_to_cache(cache_key, embedding)
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Generate a deterministic fallback embedding based on text hash
            # This ensures consistency even when API fails
            return self._generate_fallback_embedding(text)
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts, maximizing throughput.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        # Check cache for all texts
        cache_keys = [self._get_cache_key(text) for text in texts]
        cache_results = [self._get_from_cache(key) for key in cache_keys]
        
        # Identify which texts need embedding
        missing_indices = [i for i, result in enumerate(cache_results) if result is None]
        
        if not missing_indices:
            logger.debug("All embeddings found in cache")
            return cache_results
            
        # Embed missing texts
        texts_to_embed = [texts[i] for i in missing_indices]
        try:
            new_embeddings = self.openai_service.get_embeddings(texts_to_embed)
            
            # Update the cache with new embeddings
            for i, embedding in zip(missing_indices, new_embeddings):
                self._add_to_cache(cache_keys[i], embedding)
                cache_results[i] = embedding
                
            return cache_results
        except Exception as e:
            logger.error(f"Error getting batch embeddings: {str(e)}")
            # Generate fallback embeddings for missing items
            for i in missing_indices:
                cache_results[i] = self._generate_fallback_embedding(texts[i])
            return cache_results
    
    def _get_cache_key(self, text: str) -> str:
        """Generate a deterministic cache key from text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[List[float]]:
        """Retrieve an embedding from cache if it exists and isn't expired."""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() - entry['timestamp'] < self.cache_ttl:
                return entry['embedding']
            else:
                # Expired entry
                del self._cache[key]
        return None
    
    def _add_to_cache(self, key: str, embedding: List[float]) -> None:
        """Add an embedding to the cache with current timestamp."""
        self._cache[key] = {
            'embedding': embedding,
            'timestamp': datetime.utcnow()
        }
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Generate a deterministic fallback embedding when API calls fail.
        
        This ensures consistent behavior even during API outages.
        
        Args:
            text: The text to create a fallback embedding for
            
        Returns:
            A deterministic pseudo-random embedding vector
        """
        # Use text hash as random seed
        import random
        text_hash = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        random.seed(text_hash)
        
        # OpenAI's text-embedding-ada-002 has 1536 dimensions
        return [random.uniform(-1, 1) for _ in range(1536)]

# Singleton instance for application-wide use
embedding_service = EmbeddingService()