# Update app/api/main.py to include the new routers

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

# NEW IMPORTS
from app.api.endpoints.live_updates import router as live_updates_router
from app.api.endpoints.admin_monitoring import router as admin_monitoring_router
from app.api.endpoints.voice_logs_enhancement import router as voice_logs_enhancement_router

# NEW: Import Base and engine to create tables as fallback.
from app.infrastructure.database.models import Base
from app.infrastructure.database.session import engine

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

# NEW ROUTERS
app.include_router(live_updates_router, prefix="/api", tags=["Real-time Updates"])
app.include_router(admin_monitoring_router, prefix="/api/admin", tags=["Admin", "Monitoring"])
app.include_router(voice_logs_enhancement_router, prefix="/api/voice-logs", tags=["Voice Logs"])

@app.get("/")
def root():
    return {"message": "Welcome to the CRAVE Trinity Backend API"}

@app.on_event("startup")
def on_startup():
    from app.api.dependencies import init_db
    init_db()
    # Fallback: Create all tables if they don't exist.
    Base.metadata.create_all(bind=engine)
    print("Startup complete: Database and other resources initialized.")