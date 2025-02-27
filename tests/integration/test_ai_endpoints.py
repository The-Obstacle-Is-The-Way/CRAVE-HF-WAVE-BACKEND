# tests/integration/test_ai_endpoints.py
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

@pytest.mark.integration
@patch("app.core.services.rag_service.generate_personalized_insight")
def test_insights_endpoint(mock_rag):
    mock_rag.return_value = "Mocked response about cravings."

    payload = {
        "user_id": 1,
        "query": "Why do I crave sugar at night?",
        "persona": "NighttimeBinger"
    }
    response = client.post("/ai/insights", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["answer"] == "Mocked response about cravings."
