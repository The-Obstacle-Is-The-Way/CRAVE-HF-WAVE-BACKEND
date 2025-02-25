# crave_trinity_backend/app/api/main.py
from fastapi import FastAPI, APIRouter
from app.api.endpoints import health, craving_logs, ai_endpoints
from app.infrastructure.vector_db.pinecone_client import init_pinecone

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.
    
    This is the entry point for the CRAVE Trinity Backend,
    following clean architecture principles where:
    - API layer is responsible only for HTTP interactions
    - Core business logic is isolated in use cases
    - Infrastructure concerns are separated from domain logic
    """
    app = FastAPI(
        title="CRAVE Trinity Backend",
        description="Backend for craving analytics and AI-powered insights",
        version="0.1.0",
        docs_url="/docs",  # Explicit declaration of Swagger UI endpoint
        redoc_url="/redoc"  # ReDoc alternative documentation
    )
    
    # Create API router with /api prefix
    api_router = APIRouter(prefix="/api")
    
    # Include all endpoint routers
    api_router.include_router(health.router, tags=["Health"])
    api_router.include_router(craving_logs.router, tags=["Cravings"])
    api_router.include_router(ai_endpoints.router, tags=["AI"])
    
    # Add the API router to the main app
    app.include_router(api_router)
    
    # Also include routes at root level for backward compatibility
    # and simpler direct access
    app.include_router(health.router, tags=["Health"])
    app.include_router(craving_logs.router, tags=["Cravings"])
    app.include_router(ai_endpoints.router, tags=["AI"])

    @app.on_event("startup")
    def startup_event():
        """
        Executes when the application starts.
        Initializes external dependencies like Pinecone.
        """
        init_pinecone()
        print("CRAVE Trinity Backend started successfully!")

    return app

# Create the application instance
app = create_app()

# This allows running the application directly with 'python app/api/main.py'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
