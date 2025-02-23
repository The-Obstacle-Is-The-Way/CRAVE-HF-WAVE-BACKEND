# crave_trinity_backend/app/api/main.py
from fastapi import FastAPI
from app.api.endpoints import health, craving_logs
from app.infrastructure.vector_db.pinecone_client import init_pinecone

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.
    
    Routers are included and startup events are defined here.
    """
    app = FastAPI(
        title="CRAVE Trinity Backend",
        description="Backend for craving analytics",
        version="0.1.0"
    )
    app.include_router(health.router)
    app.include_router(craving_logs.router)

    @app.on_event("startup")
    def startup_event():
        # Initialize Pinecone on startup
        init_pinecone()

    return app

app = create_app()
