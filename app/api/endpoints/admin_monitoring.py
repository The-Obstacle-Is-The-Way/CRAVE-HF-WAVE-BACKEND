# File: app/api/endpoints/admin_monitoring.py

import os
import logging
import psutil
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel, CravingModel, Base
from app.infrastructure.auth.auth_service import AuthService
from app.config.settings import Settings

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the router
router = APIRouter()

# Helper function to check if user is admin
def is_admin(user: UserModel) -> bool:
    """Check if the user has admin privileges."""
    # In a real app, you might have an 'is_admin' field or role-based access
    # For simplicity, we're checking if user ID is 1 (first user)
    return user.id == 1

# Admin-only dependency
def admin_only(current_user: UserModel = Depends(AuthService().get_current_user)):
    """Dependency to ensure only admins can access the endpoint."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required."
        )
    return current_user


@router.get("/logs", tags=["Admin"])
async def get_application_logs(
    lines: int = Query(100, ge=1, le=10000, description="Number of log lines to return"),
    admin_user: UserModel = Depends(admin_only)
):
    """
    Retrieve recent application logs.
    
    This endpoint returns the last N lines from the application log file.
    Requires admin privileges.
    
    Args:
        lines: Number of log lines to return (default: 100, max: 10000)
        
    Returns:
        dict: A dictionary containing log entries and metadata
    """
    try:
        settings = Settings()
        log_file_path = settings.LOG_FILE_PATH or "app.log"
        
        if not os.path.exists(log_file_path):
            return {
                "status": "warning",
                "message": f"Log file not found at {log_file_path}",
                "logs": []
            }
        
        # Read the last N lines from the log file
        with open(log_file_path, 'r') as file:
            all_lines = file.readlines()
            log_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "log_file": log_file_path,
            "lines_requested": lines,
            "lines_returned": len(log_lines),
            "logs": log_lines
        }
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve logs: {str(e)}"
        )


@router.get("/metrics", tags=["Admin"])
async def get_system_metrics(
    admin_user: UserModel = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """
    Get system and application metrics.
    
    This endpoint provides various metrics including:
    - System resources (CPU, memory, disk)
    - Database statistics
    - User and craving counts
    - Request rates and performance metrics
    
    Requires admin privileges.
    
    Returns:
        dict: A dictionary of metrics and their values
    """
    try:
        # System metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - psutil.boot_time()
        }
        
        # Database metrics
        db_metrics = {}
        
        # Get table counts
        try:
            # Count users
            user_count = db.query(func.count(UserModel.id)).scalar()
            db_metrics["total_users"] = user_count
            
            # Count active users in the last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_users = db.query(func.count(UserModel.id)).filter(
                UserModel.last_login_at >= thirty_days_ago
            ).scalar()
            db_metrics["active_users_30d"] = active_users or 0
            
            # Count cravings
            craving_count = db.query(func.count(CravingModel.id)).scalar()
            db_metrics["total_cravings"] = craving_count
            
            # Get cravings in the last 24 hours
            day_ago = datetime.utcnow() - timedelta(days=1)
            recent_cravings = db.query(func.count(CravingModel.id)).filter(
                CravingModel.created_at >= day_ago
            ).scalar()
            db_metrics["cravings_24h"] = recent_cravings or 0
            
            # Get average intensity
            avg_intensity = db.query(func.avg(CravingModel.intensity)).scalar()
            db_metrics["avg_intensity"] = round(float(avg_intensity), 2) if avg_intensity else 0
            
        except Exception as e:
            logger.error(f"Error collecting DB metrics: {str(e)}")
            db_metrics["error"] = str(e)
        
        # Application metrics
        app_metrics = {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "version": "0.1.0",  # You might want to get this from a config or package
            "api_requests_total": 0,  # This would need request counting middleware
            "api_errors_total": 0     # This would need error tracking middleware
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_metrics,
            "database": db_metrics,
            "application": app_metrics
        }
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


@router.get("/health-detailed", tags=["Admin"])
async def detailed_health_check(
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(admin_only)
):
    """
    Perform a detailed health check of all system components.
    
    Checks:
    - Database connectivity
    - File system access
    - Memory usage
    - External service connectivity (if applicable)
    
    Requires admin privileges.
    
    Returns:
        dict: The health status of each component
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database connectivity
    try:
        # Simple query to test database connection
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "ok",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "error"
        health_status["components"]["database"] = {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # Check file system
    try:
        temp_file_path = "/tmp/health_check_test.txt"
        with open(temp_file_path, "w") as f:
            f.write("test")
        os.remove(temp_file_path)
        health_status["components"]["filesystem"] = {
            "status": "ok",
            "message": "File system is writable"
        }
    except Exception as e:
        health_status["status"] = "warning"
        health_status["components"]["filesystem"] = {
            "status": "warning",
            "message": f"File system check failed: {str(e)}"
        }
    
    # Memory usage check
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health_status["status"] = "warning"
            health_status["components"]["memory"] = {
                "status": "warning",
                "message": f"High memory usage: {memory.percent}%",
                "details": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                }
            }
        else:
            health_status["components"]["memory"] = {
                "status": "ok",
                "message": f"Memory usage: {memory.percent}%",
                "details": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                }
            }
    except Exception as e:
        health_status["components"]["memory"] = {
            "status": "unknown",
            "message": f"Memory check failed: {str(e)}"
        }
    
    return health_status