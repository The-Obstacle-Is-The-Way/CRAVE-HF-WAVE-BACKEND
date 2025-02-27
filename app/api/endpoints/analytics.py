# app/api/endpoints/analytics.py
"""
Analytics endpoints for CRAVE Trinity Backend.

Provides endpoints for analyzing craving patterns and generating insights.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import statistics
from collections import defaultdict
from pydantic import BaseModel, ConfigDict  # Import ConfigDict

# Import database dependencies
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import CravingModel

router = APIRouter()

# Database dependency
def get_db():
    """Provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def has_column(db, table_name, column_name):
    """Check if a table has a specific column."""
    try:
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False

class AnalyticsResponse(BaseModel):
    user_id: int
    period: str
    total_cravings: Optional[int] = 0
    average_intensity: Optional[float] = 0
    max_intensity: Optional[int] = 0
    min_intensity: Optional[int] = 0
    std_deviation: Optional[float] = 0
    message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PatternAnalyticsResponse(BaseModel):
    user_id: int
    period: str
    total_cravings: int = 0
    day_of_week_distribution: Optional[Dict[str, int]] = None  # Corrected type
    peak_days: Optional[List[str]] = None  # Corrected type
    insights: Optional[List[str]] = None # Correct type
    message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TimeOfDayAnalyticsResponse(BaseModel):
    user_id: int
    period: str
    total_cravings: int
    time_distribution: Dict[str, int]  # Corrected type
    average_intensity_by_time: Dict[str, float] # Corrected Type
    peak_time: Optional[str] = None
    insights: List[str]
    message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class IntensityAnalyticsResponse(BaseModel):
    user_id: int
    period: str
    average_intensity: Optional[float] = 0
    intensity_trend: str
    daily_averages: Dict[str, float]  # Corrected type
    insights: List[str]
    message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


@router.get("/user/{user_id}/summary", response_model=AnalyticsResponse)
async def get_user_craving_summary(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> AnalyticsResponse: #NEW
    """Get a summary of a user's craving patterns."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    has_user_id = has_column(db, "cravings", "user_id")

    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    )
    if has_user_id:
        query = query.filter(CravingModel.user_id == user_id)

    cravings = query.all()

    if not cravings:
        return AnalyticsResponse(
            user_id=user_id,
            period=f"Last {days} days",
            message="No cravings recorded in this period."
        )

    intensities = [c.intensity for c in cravings]
    avg_intensity = sum(intensities) / len(intensities) if intensities else 0

    return AnalyticsResponse(
        user_id=user_id,
        period=f"Last {days} days",
        total_cravings=len(cravings),
        average_intensity=round(avg_intensity, 1),
        max_intensity=max(intensities) if intensities else 0,
        min_intensity=min(intensities) if intensities else 0,
        std_deviation=round(statistics.stdev(intensities), 2) if len(intensities) > 1 else 0
    )


@router.get("/user/{user_id}/patterns", response_model=PatternAnalyticsResponse)
async def get_craving_patterns(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> PatternAnalyticsResponse: #NEW
    """Analyze patterns in a user's cravings."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    has_user_id = has_column(db, "cravings", "user_id")

    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    )
    if has_user_id:
        query = query.filter(CravingModel.user_id == user_id)

    cravings = query.all()

    if not cravings:
        return PatternAnalyticsResponse(
            user_id=user_id,
            period=f"Last {days} days",
            message="Insufficient data to detect patterns."
        )

    day_of_week_counts = defaultdict(int)
    for craving in cravings:
        day_name = craving.created_at.strftime("%A")
        day_of_week_counts[day_name] += 1

    sorted_days = sorted(day_of_week_counts.items(), key=lambda x: x[1], reverse=True)

    if sorted_days:
        peak_count = sorted_days[0][1]
        peak_days = [day for day, count in sorted_days if count == peak_count]
    else:
        peak_days = []

    return PatternAnalyticsResponse(
        user_id=user_id,
        period=f"Last {days} days",
        total_cravings=len(cravings),
        day_of_week_distribution=dict(day_of_week_counts),
        peak_days=peak_days,
        insights=generate_insights(cravings, peak_days)  # Corrected call
    )


@router.get("/user/{user_id}/time-of-day", response_model=TimeOfDayAnalyticsResponse)
async def get_time_of_day_analysis(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> TimeOfDayAnalyticsResponse: #NEW
    """Analyze cravings by time of day."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    has_user_id = has_column(db, "cravings", "user_id")

    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    )
    if has_user_id:
        query = query.filter(CravingModel.user_id == user_id)

    cravings = query.all()

    if not cravings:
        return TimeOfDayAnalyticsResponse(
            user_id=user_id,
            period=f"Last {days} days",
            time_distribution={},  # Provide empty dicts
            average_intensity_by_time={},
            insights=[],
            message="No cravings recorded in this period."
        )

    time_segments = {
        "morning": (6, 12),
        "afternoon": (12, 18),
        "evening": (18, 24),
        "night": (0, 6)
    }

    segment_counts = {segment: 0 for segment in time_segments}
    segment_intensities = {segment: [] for segment in time_segments}

    for craving in cravings:
        hour = craving.created_at.hour
        for segment, (start, end) in time_segments.items():
            if start <= hour < end:
                segment_counts[segment] += 1
                segment_intensities[segment].append(craving.intensity)
                break

    avg_intensities = {
        segment: round(sum(intensities) / len(intensities), 1) if intensities else 0
        for segment, intensities in segment_intensities.items()
    }

    peak_segment = max(segment_counts.items(), key=lambda x: x[1])[0] if segment_counts else None

    insights = []
    if peak_segment:
        insights.append(f"You experience most cravings during the {peak_segment} ({segment_counts[peak_segment]} cravings).")
        highest_intensity_segment = max(avg_intensities.items(), key=lambda x: x[1])[0] if avg_intensities else None
        if highest_intensity_segment and avg_intensities[highest_intensity_segment] > 0:
            insights.append(f"Your {highest_intensity_segment} cravings tend to be the most intense (avg: {avg_intensities[highest_intensity_segment]}).")

    return TimeOfDayAnalyticsResponse(
        user_id=user_id,
        period=f"Last {days} days",
        total_cravings=len(cravings),
        time_distribution=segment_counts,
        average_intensity_by_time=avg_intensities,
        peak_time=peak_segment,
        insights=insights
    )


@router.get("/user/{user_id}/intensity", response_model=IntensityAnalyticsResponse)
async def get_intensity_analysis(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
) -> IntensityAnalyticsResponse:
    """Analyze intensity patterns in a user's cravings."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    has_user_id = has_column(db, "cravings", "user_id")

    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    )
    if has_user_id:
        query = query.filter(CravingModel.user_id == user_id)

    cravings = query.all()
    cravings.sort(key=lambda c: c.created_at)

    if not cravings:
        return IntensityAnalyticsResponse(
            user_id=user_id,
            period=f"Last {days} days",
            daily_averages={},  # Provide empty dict
            insights=[],
            message="No cravings recorded in this period."
        )

    daily_intensities = defaultdict(list)
    for craving in cravings:
        date_str = craving.created_at.strftime("%Y-%m-%d")
        daily_intensities[date_str].append(craving.intensity)

    daily_averages = {
        date: round(sum(intensities) / len(intensities), 1)
        for date, intensities in daily_intensities.items()
    }

    trend = "stable"
    if len(daily_averages) >= 7:
        dates = sorted(daily_averages.keys())
        first_week_avg = sum(daily_averages[d] for d in dates[:7]) / 7
        last_week_avg = sum(daily_averages[d] for d in dates[-7:]) / 7
        diff = last_week_avg - first_week_avg
        if diff > 1:
            trend = "increasing"
        elif diff < -1:
            trend = "decreasing"

    insights = []
    if trend == "increasing":
        insights.append("Your craving intensity has been increasing over time.")
    elif trend == "decreasing":
        insights.append("Your craving intensity has been decreasing over time.")
    else:
        insights.append("Your craving intensity has remained relatively stable.")

    return IntensityAnalyticsResponse(
        user_id=user_id,
        period=f"Last {days} days",
        average_intensity=round(sum(c.intensity for c in cravings) / len(cravings), 1),
        intensity_trend=trend,
        daily_averages=daily_averages,
        insights=insights
    )

def generate_insights(cravings, peak_days):
    """Generate insights based on craving patterns."""
    insights = []

    if peak_days:
        if len(peak_days) == 1:
            insights.append(f"You experience most cravings on {peak_days[0]}.")
        elif len(peak_days) == 2:
            insights.append(f"You experience most cravings on {peak_days[0]} and {peak_days[1]}.")
        else:
            days_str = ", ".join(peak_days[:-1]) + " and " + peak_days[-1]
            insights.append(f"Your cravings are distributed across {days_str}.")

    intensities = [c.intensity for c in cravings]
    if intensities:
        avg_intensity = sum(intensities) / len(intensities)
        if avg_intensity > 7:
            insights.append("Your cravings tend to be quite intense (>7/10 on average).")
        elif avg_intensity < 4:
            insights.append("Your cravings are generally mild (<4/10 on average).")

    return insights