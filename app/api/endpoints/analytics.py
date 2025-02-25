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
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

# Import database dependencies
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import CravingModel

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

def has_column(db, table_name, column_name):
    """Check if a table has a specific column in the database."""
    try:
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False

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
    
    # Check if user_id column exists
    has_user_id = has_column(db, "cravings", "user_id")
    
    # Query cravings within the date range
    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    )
    
    # Add user_id filter only if the column exists
    if has_user_id:
        query = query.filter(CravingModel.user_id == user_id)
    
    cravings = query.all()
    
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
    """
    # Calculate the date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Check if user_id column exists
    has_user_id = has_column(db, "cravings", "user_id")
    
    # Query cravings within the date range
    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.created_at >= start_date,
        CravingModel.created_at <= end_date
    )
    
    # Add user_id filter only if the column exists
    if has_user_id:
        query = query.filter(CravingModel.user_id == user_id)
    
    cravings = query.all()
    
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
    db: Session = Depend