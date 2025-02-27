# crave_trinity_backend/tests/integration/test_craving_search_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.api.main import app

client = TestClient(app)

@pytest.mark.integration
@patch("app.infrastructure.external.openai_embedding.openai.Embedding.create")
@patch("app.infrastructure.vector_db.vector_repository.get_pinecone_index")
def test_cravings_search_endpoint(mock_get_index, mock_create_embedding):
    mock_create_embedding.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}]
    }
    mock_index = MagicMock()
    mock_index.query.return_value.matches = [
        MagicMock(id="42", score=0.97, metadata={"user_id":1})
    ]
    mock_get_index.return_value = mock_index

    response = client.get("/cravings/search", params={"user_id":1, "query_text":"chocolate"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["craving_id"] == 42
    assert data["results"][0]["score"] == 0.97
