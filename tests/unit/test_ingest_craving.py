# crave_trinity_backend/tests/unit/test_ingest_craving.py
import pytest
from datetime import datetime
from app.core.entities.craving import Craving
from app.core.use_cases.ingest_craving import (
    IngestCravingInput,
    ingest_craving,
)
from app.infrastructure.database.repository import CravingRepository

class MockCravingRepository:
    def create_craving(self, domain_craving: Craving) -> Craving:
        # Just fake it
        return Craving(
            id=123,
            user_id=domain_craving.user_id,
            description=domain_craving.description,
            intensity=domain_craving.intensity,
            created_at=datetime.utcnow()
        )

@pytest.mark.unit
def test_ingest_craving_use_case():
    repo = MockCravingRepository()
    input_dto = IngestCravingInput(
        user_id=1,
        description="Test craving",
        intensity=5
    )
    result = ingest_craving(input_dto, repo)
    assert result.id == 123
    assert result.user_id == 1
    assert result.description == "Test craving"
    assert result.intensity == 5
