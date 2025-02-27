# app/api/main.py
from fastapi import FastAPI
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.user_queries import router as user_queries_router
from app.api.endpoints.craving_logs import router as craving_logs_router
from app.api.endpoints.ai_endpoints import router as ai_router
from app.api.endpoints.search_cravings import router as search_router
from app.api.endpoints.analytics import router as analytics_router
from app.api.endpoints.voice_logs_endpoints import router as voice_logs_router
from app.api.endpoints.auth_endpoints import router as auth_router
from app.api.endpoints.live_updates import router as live_updates_router
from app.api.endpoints.admin_monitoring import router as admin_monitoring_router
from app.api.endpoints.voice_logs_enhancement import router as voice_logs_enhancement_router

# Import Base and engine to create tables as fallback.
from app.infrastructure.database.models import Base
from sqlalchemy import create_engine
import os

# Direct connection to Railway PostgreSQL
# We're explicitly setting this to ensure it uses the right connection string
db_url = os.environ.get("DATABASE_URL")
if db_url and "railway" in db_url:
    # Print connection info for debugging (masking password)
    safe_url = db_url.replace(db_url.split("@")[0], "postgresql://****:****")
    print(f"Using database URL: {safe_url}")
    
    # Create engine with SSL for Railway
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}
    )
else:
    # Fall back to local for development
    print("WARNING: No DATABASE_URL found in environment, using local database")
    engine = create_engine("postgresql://postgres:password@localhost:5432/crave_db")

app = FastAPI(
    title="CRAVE Trinity Backend",
    description="A modular, AI-powered backend for craving analytics",
    version="0.1.0"
)

app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(user_queries_router, prefix="/api/cravings", tags=["Cravings"])
app.include_router(craving_logs_router, prefix="/api/cravings", tags=["Cravings"])
app.include_router(ai_router, prefix="/api", tags=["AI"])
app.include_router(search_router, prefix="/api/cravings", tags=["Cravings"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(voice_logs_router, prefix="/api/voice-logs", tags=["Voice Logs"])
app.include_router(live_updates_router, prefix="/api", tags=["Real-time Updates"])
app.include_router(admin_monitoring_router, prefix="/api/admin", tags=["Admin", "Monitoring"])
app.include_router(voice_logs_enhancement_router, prefix="/api/voice-logs", tags=["Voice Logs"])

@app.get("/")
def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to the CRAVE Trinity Backend API"}

@app.get("/debug")
def debug_info():
    """Debug endpoint to check environment configuration."""
    return {
        "database_configured": bool(db_url),
        "database_type": "Railway PostgreSQL" if db_url and "railway" in db_url else "Local/Other",
        "env_vars_set": {
            "DATABASE_URL": bool(os.environ.get("DATABASE_URL")),
            "PINECONE_API_KEY": bool(os.environ.get("PINECONE_API_KEY")),
            "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
            "HUGGINGFACE_API_KEY": bool(os.environ.get("HUGGINGFACE_API_KEY")),
        }
    }

@app.on_event("startup")
def on_startup():
    """Application startup event handler."""
    # Print environment variables for debugging
    print("==== CHECKING ENVIRONMENT VARIABLES ====")
    print(f"DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}")
    print(f"PINECONE_API_KEY set: {bool(os.environ.get('PINECONE_API_KEY'))}")
    print(f"OPENAI_API_KEY set: {bool(os.environ.get('OPENAI_API_KEY'))}")
    print(f"HUGGINGFACE_API_KEY set: {bool(os.environ.get('HUGGINGFACE_API_KEY'))}")
    
    try:
        # Create tables directly
        print("Attempting to create database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
    
    print("Startup complete: Ready to handle requests.")