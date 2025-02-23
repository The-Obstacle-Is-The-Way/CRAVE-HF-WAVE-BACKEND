# crave_trinity_backend/tests/unit/test_search_cravings.py

import pytest
from unittest.mock import patch, MagicMock
from app.core.use_cases.search_cravings import (
    search_cravings, 
    SearchCravingsInput
)

@pytest.mark.unit
@patch("app.infrastructure.external.openai_embedding.openai.Embedding.create")
@patch("app.infrastructure.vector_db.vector_repository.get_pinecone_index")
def test_search_cravings(mock_get_index, mock_create_embedding):
    # Mock the openai embedding response
    mock_create_embedding.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }
    # Mock the pinecone index query
    mock_index = MagicMock()
    mock_index.query.return_value.matches = [
        MagicMock(id="42", score=0.85, metadata={"user_id":1})
    ]
    mock_get_index.return_value = mock_index

    input_dto = SearchCravingsInput(
        user_id=1, 
        query_text="chocolate cravings", 
        top_k=3
    )
    results = search_cravings(input_dto)
    assert len(results) == 1
    assert results[0].craving_id == 42
    assert results[0].score == 0.85
    assert results[0].metadata["user_id"] == 1
