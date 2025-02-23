# crave_trinity_backend/app/api/main.py

from fastapi import FastAPI
from app.api.endpoints import health
from app.config.settings import Settings  # We'll define this next

def create_app() -> FastAPI:
    app = FastAPI(
        title="CRAVE Trinity Backend",
        description="Clean Architecture FastAPI Backend for CRAVE",
        version="0.1.0",
    )

    # Include endpoints
    app.include_router(health.router)

    return app

settings = Settings()
app = create_app()

# For local dev run:
# uvicorn app.api.main:app --reload
