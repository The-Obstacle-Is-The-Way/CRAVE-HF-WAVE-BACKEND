# crave_trinity_backend/app/core/services/pattern_detection_service.py
"""
Pattern detection service for analyzing craving patterns.

This service implements algorithms to detect patterns in craving history:
- Time-based patterns (time of day, day of week)
- Intensity trends
- Correlations with external factors
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.core.entities.craving import Craving

@dataclass
class PatternInsight:
    """A detected pattern in craving behavior."""
    pattern_type: str
    description: str
    confidence: float
    relevant_cravings: List[int]

def detect_patterns(cravings: List[Craving], timeframe_days: int) -> List[PatternInsight]:
    """
    Analyze craving history to detect behavioral patterns.
    
    Args:
        cravings: List of user craving entries
        timeframe_days: Analysis timeframe in days
        
    Returns:
        List of detected patterns with confidence scores
    """
    # This is a placeholder for the real implementation
    # In a full implementation, this would use time series analysis
    # and statistical methods to identify real patterns
    
    # For demo/YC purposes, this returns None so we use the mock data
    return None
    
    # The real implementation would look something like:
    patterns = []
    
    # Example: Detect time-of-day patterns
    evening_cravings = [c for c in cravings if _is_evening(c.created_at)]
    if len(evening_cravings) > len(cravings) * 0.5:
        evening_ratio = len(evening_cravings) / max(1, len(cravings) - len(evening_cravings))
        patterns.append(
            PatternInsight(
                pattern_type="time_based",
                description=f"Evening cravings occur {evening_ratio:.1f}x more frequently than other times",
                confidence=min(0.9, 0.5 + evening_ratio/10),
                relevant_cravings=[c.id for c in evening_cravings[:5]]
            )
        )
    
    # Example: Detect intensity trends
    # (simplified implementation for demo)
    if len(cravings) >= 5:
        sorted_cravings = sorted(cravings, key=lambda c: c.created_at)
        first_half = sorted_cravings[:len(sorted_cravings)//2]
        second_half = sorted_cravings[len(sorted_cravings)//2:]
        
        first_avg = sum(c.intensity for c in first_half) / len(first_half)
        second_avg = sum(c.intensity for c in second_half) / len(second_half)
        
        change_pct = (second_avg - first_avg) / first_avg * 100
        if abs(change_pct) > 10:
            direction = "increased" if change_pct > 0 else "decreased"
            patterns.append(
                PatternInsight(
                    pattern_type="intensity_trend",
                    description=f"Craving intensity has {direction} by {abs(change_pct):.1f}% over the analyzed period",
                    confidence=min(0.8, 0.5 + abs(change_pct)/100),
                    relevant_cravings=[c.id for c in sorted_cravings[:5]]
                )
            )
    
    return patterns

def _is_evening(dt: datetime) -> bool:
    """Check if a datetime is in the evening (7-10 PM)."""
    return 19 <= dt.hour <= 22
