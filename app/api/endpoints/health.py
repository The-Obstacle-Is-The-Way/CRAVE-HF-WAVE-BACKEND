# crave_trinity_backend/app/api/endpoints/health.py
from fastapi import APIRouter, Response
import time
from datetime import datetime

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    """
    Simple health check endpoint to verify the API is running.
    Returns basic service information and status.
    
    Returns:
        dict: Service status information
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time(),  # You might want to track actual uptime in a real service
        "version": "0.1.0"
    }
