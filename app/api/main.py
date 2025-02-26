# File: app/api/main.py

from fastapi import FastAPI

# Existing imports
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.user_queries import router as user_queries_router
from app.api.endpoints.craving_logs import router as craving_logs_router
from app.api.endpoints.ai_endpoints import router as ai_router
from app.api.endpoints.search_cravings import router as search_router
from app.api.endpoints.analytics import router as analytics_router

# NEW: Import our auth endpoints
from app.api.endpoints.auth_endpoints import router as auth_router

app = FastAPI(
    title="CRAVE Trinity Backend",
    description="A modular, AI-powered backend for craving analytics",
    version="0.1.0"
)

# Include your new auth router
app.include_router(auth_router, prefix="/api")

# Existing routers
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(user_queries_router, prefix="/api/cravings", tags=["Cravings"])
app.include_router(craving_logs_router, prefix="/api/cravings", tags=["Cravings"])
app.include_router(ai_router, prefix="/api", tags=["AI"])
app.include_router(search_router, prefix="/api/cravings", tags=["Cravings"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {"message": "Welcome to the CRAVE Trinity Backend API"}

@app.on_event("startup")
def on_startup():
    from app.api.dependencies import init_db
    init_db()
    print("Startup complete: Database and other resources initialized.")