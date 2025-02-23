# crave_trinity_backend/tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

@pytest.mark.integration
def test_create_craving():
    payload = {
        "user_id": 1,
        "description": "Chocolate craving",
        "intensity": 8
    }
    response = client.post("/cravings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["user_id"] == 1
    assert data["description"] == "Chocolate craving"
    assert data["intensity"] == 8
    assert "created_at" in data
