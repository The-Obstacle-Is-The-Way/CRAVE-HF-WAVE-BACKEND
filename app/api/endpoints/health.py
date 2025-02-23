# crave_trinity_backend/app/api/endpoints/health.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "CRAVE backend running"}
