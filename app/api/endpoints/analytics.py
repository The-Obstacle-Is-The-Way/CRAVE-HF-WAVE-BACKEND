# File: app/api/endpoints/analytics.py
"""
Analytics endpoints for CRAVE Trinity Backend.

This module provides REST API endpoints for analyzing craving patterns,
generating insights, and visualizing user data. It follows clean architecture
principles by separating API concerns from business logic.

Endpoints:
- GET /api/analytics/user/{user_id}/summary: Get a summary of user's cravings
- GET /api/analytics/user/{user_id}/patterns: Analyze patterns in user's cravings
- GET /api/analytics/user/{user_id}/time-of-day: Analyze cravings by time of day
- GET /api/analytics/user/{user_id}/intensity: Analyze intensity patterns

Each endpoint follows the same pattern:
1. Accept request and validate parameters
2. Call the appropriate service function
3. Transform results into API response format
4. Handle errors appropriately
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

# Import database dependencies
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import CravingModel

# Import services
from app.core.services.analytics_service import analyze_patterns, list_personas

# Create router
router = APIRouter()

# Database dependency
def get_db():
    """Provide a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/user/{user_id}/summary")
async def get_user_craving_summary(
    user_id: int, 
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get a summary of a user's craving patterns.
    
    Args:
        user_id: The ID of the user
        days: Number of days to include in analysis (default 30)
        
    Returns:
        Summary statistics and insights about the user's cravings
    """
    # Calculate the date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query cravings within the date range
    cravings = db.query(CravingModel).filter(
        CravingModel.id == user_id,
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    ).all()
    
    # If no cravings found, return appropriate message
    if not cravings:
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "total_cravings": 0,
            "message": "No cravings recorded in this period."
        }
    
    # Calculate summary statistics
    intensities = [c.intensity for c in cravings]
    avg_intensity = sum(intensities) / len(intensities) if intensities else 0
    
    # Return summary data
    return {
        "user_id": user_id,
        "period": f"Last {days} days",
        "total_cravings": len(cravings),
        "average_intensity": round(avg_intensity, 1),
        "max_intensity": max(intensities) if intensities else 0,
        "min_intensity": min(intensities) if intensities else 0,
        "std_deviation": round(statistics.stdev(intensities), 2) if len(intensities) > 1 else 0
    }

@router.get("/user/{user_id}/patterns")
async def get_craving_patterns(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze patterns in a user's cravings.
    
    This endpoint detects patterns such as:
    - Frequency by day of week
    - Trends over time
    - Correlation between intensity and time
    
    Args:
        user_id: The ID of the user
        days: Number of days to include in analysis (default 30)
        
    Returns:
        Detected patterns and insights
    """
    # Calculate the date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query cravings within the date range
    cravings = db.query(CravingModel).filter(
        CravingModel.id == user_id,
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    ).all()
    
    # If no cravings found, return appropriate message
    if not cravings:
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "message": "Insufficient data to detect patterns."
        }
    
    # Analyze day of week patterns
    day_of_week_counts = defaultdict(int)
    for craving in cravings:
        day_name = craving.created_at.strftime("%A")  # Get day name (Monday, Tuesday, etc.)
        day_of_week_counts[day_name] += 1
    
    # Sort days by frequency
    sorted_days = sorted(day_of_week_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Find peak day(s)
    if sorted_days:
        peak_count = sorted_days[0][1]
        peak_days = [day for day, count in sorted_days if count == peak_count]
    else:
        peak_days = []
    
    # Return pattern analysis
    return {
        "user_id": user_id,
        "period": f"Last {days} days",
        "total_cravings": len(cravings),
        "day_of_week_distribution": dict(day_of_week_counts),
        "peak_days": peak_days,
        "insights": generate_insights(cravings, peak_days)
    }

@router.get("/user/{user_id}/time-of-day")
async def get_time_of_day_analysis(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze cravings by time of day.
    
    This endpoint breaks down cravings into time segments:
    - Morning (6am-12pm)
    - Afternoon (12pm-6pm)
    - Evening (6pm-12am)
    - Night (12am-6am)
    
    Args:
        user_id: The ID of the user
        days: Number of days to include in analysis (default 30)
        
    Returns:
        Time-based distribution and insights
    """
    # Calculate the date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query cravings within the date range
    cravings = db.query(CravingModel).filter(
        CravingModel.id == user_id,
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    ).all()
    
    # If no cravings found, return appropriate message
    if not cravings:
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "message": "No cravings recorded in this period."
        }
    
    # Define time segments
    time_segments = {
        "morning": (6, 12),    # 6am-12pm
        "afternoon": (12, 18), # 12pm-6pm
        "evening": (18, 24),   # 6pm-12am
        "night": (0, 6)        # 12am-6am
    }
    
    # Count cravings by time segment
    segment_counts = {segment: 0 for segment in time_segments}
    segment_intensities = {segment: [] for segment in time_segments}
    
    for craving in cravings:
        hour = craving.created_at.hour
        
        # Determine which segment this hour belongs to
        for segment, (start, end) in time_segments.items():
            if start <= hour < end:
                segment_counts[segment] += 1
                segment_intensities[segment].append(craving.intensity)
                break
    
    # Calculate average intensity for each segment
    avg_intensities = {}
    for segment, intensities in segment_intensities.items():
        if intensities:
            avg_intensities[segment] = round(sum(intensities) / len(intensities), 1)
        else:
            avg_intensities[segment] = 0
    
    # Find peak time segment
    peak_segment = max(segment_counts.items(), key=lambda x: x[1])[0] if segment_counts else None
    
    # Generate insights
    insights = []
    if peak_segment:
        insights.append(f"You experience most cravings during the {peak_segment} ({segment_counts[peak_segment]} cravings).")
        
        # Find highest intensity segment
        highest_intensity_segment = max(avg_intensities.items(), key=lambda x: x[1])[0] if avg_intensities else None
        if highest_intensity_segment and avg_intensities[highest_intensity_segment] > 0:
            insights.append(f"Your {highest_intensity_segment} cravings tend to be the most intense (avg: {avg_intensities[highest_intensity_segment]}).")
    
    # Return time-based analysis
    return {
        "user_id": user_id,
        "period": f"Last {days} days",
        "total_cravings": len(cravings),
        "time_distribution": segment_counts,
        "average_intensity_by_time": avg_intensities,
        "peak_time": peak_segment,
        "insights": insights
    }

@router.get("/user/{user_id}/intensity")
async def get_intensity_analysis(
    user_id: int,
    days: Optional[int] = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze intensity patterns in a user's cravings.
    
    This endpoint examines how craving intensity varies:
    - Over time (trend analysis)
    - By day of week
    - By time of day
    
    Args:
        user_id: The ID of the user
        days: Number of days to include in analysis (default 30)
        
    Returns:
        Intensity analysis and trends
    """
    # Calculate the date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query cravings within the date range
    cravings = db.query(CravingModel).filter(
        CravingModel.id == user_id,
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    ).order_by(CravingModel.created_at).all()
    
    # If no cravings found, return appropriate message
    if not cravings:
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "message": "No cravings recorded in this period."
        }
    
    # Group cravings by date for trend analysis
    daily_intensities = defaultdict(list)
    for craving in cravings:
        date_str = craving.created_at.strftime("%Y-%m-%d")
        daily_intensities[date_str].append(craving.intensity)
    
    # Calculate daily averages
    daily_averages = {
        date: round(sum(intensities) / len(intensities), 1)
        for date, intensities in daily_intensities.items()
    }
    
    # Determine if there's an upward or downward trend
    trend = "stable"
    if len(daily_averages) >= 7:  # Need at least a week of data
        dates = sorted(daily_averages.keys())
        first_week_avg = sum(daily_averages[d] for d in dates[:7]) / 7
        last_week_avg = sum(daily_averages[d] for d in dates[-7:]) / 7
        
        diff = last_week_avg - first_week_avg
        if diff > 1:
            trend = "increasing"
        elif diff < -1:
            trend = "decreasing"
    
    # Generate insights
    insights = []
    if trend == "increasing":
        insights.append("Your craving intensity has been increasing over time.")
    elif trend == "decreasing":
        insights.append("Your craving intensity has been decreasing over time.")
    else:
        insights.append("Your craving intensity has remained relatively stable.")
    
    # Return intensity analysis
    return {
        "user_id": user_id,
        "period": f"Last {days} days",
        "average_intensity": round(sum(c.intensity for c in cravings) / len(cravings), 1),
        "intensity_trend": trend,
        "daily_averages": daily_averages,
        "insights": insights
    }

# Helper function for generating insights
def generate_insights(cravings, peak_days):
    """Generate insights based on craving patterns."""
    insights = []
    
    # Add insights based on peak days
    if peak_days:
        if len(peak_days) == 1:
            insights.append(f"You experience most cravings on {peak_days[0]}.")
        elif len(peak_days) == 2:
            insights.append(f"You experience most cravings on {peak_days[0]} and {peak_days[1]}.")
        else:
            days_str = ", ".join(peak_days[:-1]) + " and " + peak_days[-1]
            insights.append(f"Your cravings are distributed across {days_str}.")
    
    # Analyze intensity patterns
    intensities = [c.intensity for c in cravings]
    if intensities:
        avg_intensity = sum(intensities) / len(intensities)
        if avg_intensity > 7:
            insights.append("Your cravings tend to be quite intense (>7/10 on average).")
        elif avg_intensity < 4:
            insights.append("Your cravings are generally mild (<4/10 on average).")
    
    return insights