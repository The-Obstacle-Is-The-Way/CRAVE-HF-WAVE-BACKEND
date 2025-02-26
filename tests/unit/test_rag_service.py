# File: tests/unit/test_rag_service.py
"""
Tests for the RAG pipeline and its components.

These tests ensure that the Retrieval-Augmented Generation pipeline works
correctly end-to-end, with proper mocking of external dependencies.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.core.services.rag_service import RAGService, RetrievedCraving
from app.core.services.embedding_service import EmbeddingService
from app.infrastructure.vector_db.vector_repository import VectorRepository
from app.infrastructure.llm.llama2_adapter import Llama2Adapter

@pytest.fixture
def mock_embedding():
    """Return a mock embedding vector."""
    return [0.1] * 1536  # OpenAI embedding size

@pytest.fixture
def mock_search_results():
    """Return mocked search results from vector database."""
    return {
        "matches": [
            {
                "id": "123",
                "score": 0.92,
                "metadata": {
                    "user_id": 1,
                    "description": "Strong chocolate craving after dinner",
                    "intensity": 8,
                    "created_at": datetime.utcnow().isoformat()
                }
            },
            {
                "id": "456",
                "score": 0.85,
                "metadata": {
                    "user_id": 1,
                    "description": "Mild sugar craving in afternoon",
                    "intensity": 5,
                    "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat()
                }
            },
            {
                "id": "789",
                "score": 0.72,
                "metadata": {
                    "user_id": 1,
                    "description": "Intense ice cream craving at night",
                    "intensity": 9,
                    "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()
                }
            }
        ]
    }

@pytest.mark.unit
class TestRAGService:
    """Tests for the RAGService class."""
    
    @patch('app.core.services.embedding_service.embedding_service.get_embedding')
    @patch('app.infrastructure.vector_db.vector_repository.VectorRepository.search_cravings')
    @patch('app.infrastructure.llm.llama2_adapter.Llama2Adapter.generate_text')
    def test_generate_personalized_insight(
        self, 
        mock_generate_text, 
        mock_search_cravings, 
        mock_get_embedding,
        mock_embedding,
        mock_search_results
    ):
        """Test the full RAG pipeline with base model."""
        # Setup mocks
        mock_get_embedding.return_value = mock_embedding
        mock_search_cravings.return_value = mock_search_results
        mock_generate_text.return_value = "This is a personalized insight about your cravings."
        
        # Initialize service
        service = RAGService()
        
        # Call the method
        result = service.generate_personalized_insight(
            user_id=1,
            query="Why do I crave chocolate at night?",
            top_k=3
        )
        
        # Verify the result
        assert result == "This is a personalized insight about your cravings."
        
        # Verify the mocks were called with expected arguments
        mock_get_embedding.assert_called_once()
        mock_search_cravings.assert_called_once()
        mock_generate_text.assert_called_once()
        
        # Verify the prompt construction (partial match)
        prompt = mock_generate_text.call_args[0][0]
        assert "Why do I crave chocolate at night?" in prompt
        assert "Strong chocolate craving after dinner" in prompt
        assert "Mild sugar craving in afternoon" in prompt
        
    @patch('app.core.services.embedding_service.embedding_service.get_embedding')
    @patch('app.infrastructure.vector_db.vector_repository.VectorRepository.search_cravings')
    @patch('app.infrastructure.llm.lora_adapter.LoRAAdapterManager.generate_text_with_adapter')
    def test_generate_with_persona(
        self, 
        mock_generate_with_adapter, 
        mock_search_cravings, 
        mock_get_embedding,
        mock_embedding,
        mock_search_results
    ):
        """Test generation with a LoRA persona."""
        # Setup mocks
        mock_get_embedding.return_value = mock_embedding
        mock_search_cravings.return_value = mock_search_results
        mock_generate_with_adapter.return_value = "Personalized insight from LoRA model."
        
        # Patch settings to include test persona
        with patch('app.config.settings.Settings.LORA_PERSONAS', {"TestPersona": "path/to/adapter"}):
            # Initialize service
            service = RAGService()
            
            # Call the method with persona
            result = service.generate_personalized_insight(
                user_id=1,
                query="What triggers my food cravings?",
                persona="TestPersona"
            )
            
            # Verify the result
            assert result == "Personalized insight from LoRA model."
            
            # Verify LoRA adapter was called
            mock_generate_with_adapter.assert_called_once()
            
    def test_process_search_results(self):
        """Test processing of raw search results into domain objects."""
        service = RAGService()
        processed = service._process_search_results(mock_search_results())
        
        # Check conversion to domain objects
        assert len(processed) == 3
        assert all(isinstance(craving, RetrievedCraving) for craving in processed)
        assert processed[0].id == 123
        assert processed[0].description == "Strong chocolate craving after dinner"
        assert processed[0].intensity == 8
        
    def test_time_weighting(self):
        """Test time-weighted scoring of cravings."""
        service = RAGService()
        
        # Create test cravings with different ages
        cravings = [
            RetrievedCraving(
                id=1,
                description="Recent craving",
                created_at=datetime.utcnow() - timedelta(days=5),
                intensity=7,
                score=0.9
            ),
            RetrievedCraving(
                id=2,
                description="Older craving",
                created_at=datetime.utcnow() - timedelta(days=60),
                intensity=8,
                score=0.95
            ),
            RetrievedCraving(
                id=3,
                description="Very old craving",
                created_at=datetime.utcnow() - timedelta(days=120),
                intensity=9,
                score=0.85
            )
        ]
        
        # Apply time weighting
        weighted = service._apply_time_weighting(cravings, recency_boost_days=30)
        
        # Verify weighting was applied
        assert weighted[0].time_score == 1.0  # Recent should get full score
        assert weighted[1].time_score < 1.0  # Older should get reduced score
        assert weighted[2].time_score < weighted[1].time_score  # Very old should get lowest score
        
        # Verify sorting
        assert weighted[0].id == 1  # Recent craving should come first despite lower base score
        
    def test_construct_prompt(self):
        """Test prompt construction with retrieved cravings."""
        service = RAGService()
        query = "Why do I crave sugary foods at night?"
        
        # Create test cravings
        cravings = [
            RetrievedCraving(
                id=1,
                description="Chocolate craving after dinner",
                created_at=datetime.utcnow(),
                intensity=8,
                score=0.9
            ),
            RetrievedCraving(
                id=2,
                description="Ice cream craving at night",
                created_at=datetime.utcnow() - timedelta(days=1),
                intensity=7,
                score=0.85
            )
        ]
        
        # Construct prompt
        prompt = service._construct_prompt(user_id=1, query=query, retrieved_cravings=cravings)
        
        # Verify prompt contains expected elements
        assert "USER PROFILE:" in prompt
        assert "User ID: 1" in prompt
        assert "Why do I crave sugary foods at night?" in prompt
        assert "Chocolate craving after dinner" in prompt
        assert "Ice cream craving at night" in prompt
        assert "Intensity: 8/10" in prompt
        
    def test_empty_results_handling(self):
        """Test handling of empty search results."""
        service = RAGService()
        
        # Construct prompt with no cravings
        prompt = service._construct_prompt(user_id=1, query="Test query", retrieved_cravings=[])
        
        # Verify appropriate message is included
        assert "No relevant craving data found" in prompt
        
    @patch('app.core.services.embedding_service.embedding_service.get_embedding')
    @patch('app.infrastructure.vector_db.vector_repository.VectorRepository.search_cravings')
    @patch('app.infrastructure.llm.llama2_adapter.Llama2Adapter.generate_text')
    def test_error_handling(
        self, 
        mock_generate_text, 
        mock_search_cravings, 
        mock_get_embedding
    ):
        """Test error handling in the RAG pipeline."""
        # Setup mocks to raise exception
        mock_get_embedding.side_effect = Exception("Embedding API error")
        
        # Initialize service
        service = RAGService()
        
        # Call the method - should not raise exception
        result = service.generate_personalized_insight(
            user_id=1,
            query="Why do I crave chocolate?",
            top_k=3
        )
        
        # Verify graceful error handling
        assert "trouble" in result.lower()
        assert "try again" in result.lower()


@pytest.mark.unit
class TestEmbeddingService:
    """Tests for the EmbeddingService."""
    
    def test_cache_functionality(self):
        """Test the caching functionality of the embedding service."""
        service = EmbeddingService()
        test_text = "This is a test text"
        cache_key = service._get_cache_key(test_text)
        
        # Initially cache should be empty
        assert service._get_from_cache(cache_key) is None
        
        # Add to cache
        test_embedding = [0.1, 0.2, 0.3]
        service._add_to_cache(cache_key, test_embedding)
        
        # Now should be in cache
        cached = service._get_from_cache(cache_key)
        assert cached is not None
        assert cached == test_embedding
        
    @patch('app.infrastructure.external.openai_embedding.OpenAIEmbeddingService.embed_text')
    def test_get_embedding_with_cache(self, mock_embed_text):
        """Test that embeddings are cached and reused."""
        mock_embed_text.return_value = [0.1, 0.2, 0.3]
        
        service = EmbeddingService()
        test_text = "This is a test text"
        
        # First call should use the API
        first_result = service.get_embedding(test_text)
        assert mock_embed_text.call_count == 1
        
        # Second call should use cache
        second_result = service.get_embedding(test_text)
        assert mock_embed_text.call_count == 1  # Still only called once
        assert first_result == second_result
        
    @patch('app.infrastructure.external.openai_embedding.OpenAIEmbeddingService.get_embeddings')
    def test_batch_embeddings(self, mock_get_embeddings):
        """Test batch embedding functionality."""
        mock_get_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        service = EmbeddingService()
        texts = ["Text 1", "Text 2"]
        
        # Get batch embeddings
        results = service.get_batch_embeddings(texts)
        
        # Verify results
        assert len(results) == 2
        assert results[0] == [0.1, 0.2]
        assert results[1] == [0.3, 0.4]
        
        # Second call should use cache
        mock_get_embeddings.reset_mock()
        cached_results = service.get_batch_embeddings(texts)
        assert mock_get_embeddings.call_count == 0
        assert cached_results == results
        
    @patch('app.infrastructure.external.openai_embedding.OpenAIEmbeddingService.embed_text')
    def test_error_handling(self, mock_embed_text):
        """Test error handling with fallback embeddings."""
        mock_embed_text.side_effect = Exception("API Error")
        
        service = EmbeddingService()
        test_text = "This is a test"
        
        # Should not raise exception
        result = service.get_embedding(test_text)
        
        # Should get a fallback embedding of correct size
        assert len(result) == 1536  # Expected OpenAI dimension
        
        # Same text should get same fallback
        second_result = service.get_embedding(test_text)
        assert result == second_result