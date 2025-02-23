# crave_trinity_backend/app/api/main.py
from fastapi import FastAPI
from app.api.endpoints import health
from app.api.endpoints import craving_logs  # NEW
from app.config.settings import Settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="CRAVE Trinity Backend",
        description="Clean Architecture FastAPI Backend for CRAVE",
        version="0.2.0",
    )

    # Existing health router
    app.include_router(health.router)

    # NEW: Include cravings router
    app.include_router(craving_logs.router)

    return app

settings = Settings()
app = create_app()
