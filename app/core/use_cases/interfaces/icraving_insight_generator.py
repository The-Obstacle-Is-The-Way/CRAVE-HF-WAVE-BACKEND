# File: app/core/use_cases/interfaces/icraving_insight_generator.py
from abc import ABC, abstractmethod
from typing import Optional

class ICravingInsightGenerator(ABC):
    """
    Interface for generating craving insights from user history and/or queries.
    """

    @abstractmethod
    def generate_insights(self, user_id: int, query: Optional[str] = None) -> str:
        """
        Generate a textual summary of insights for a given user, optionally focused on a query.
        """
        pass
