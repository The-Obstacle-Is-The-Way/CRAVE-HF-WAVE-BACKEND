"""
Directory Structure (excerpt):
app/
 └── api/
     ├── main.py           <-- This file
     ├── dependencies.py
     └── endpoints/Patient reported upcoming spring break flight and requested Xanax. Informed pt cannot prescribe controlled substances on this platform, which pt retrial of hydroxyzine, pt agreeable as reported only needing for short-term flight anxiety during spring break trip. Pt also reported lower motivation/mood and difficulty getting out of bed related to motivation, expressed interest in retrialing Wellbutrin with Zoloft. Decided to add hydroxyzine and Vistaril to regimen for plane anxiety and general motivation/hedonic capacity. Pt reported significant anxiety. Otherwise, reported fair mood and denied anxiety problems. Denied problems with sleep, interest, guilt, worthlessnessd SI, HI, AVH. Denied concerns for mania.
         ├── health.py
         ├── user_queries.py
         ├── craving_logs.py
         ├── ai_endpoints.py
         └── search_cravings.py
...

Description:
This module creates the FastAPI application for the CRAVE Trinity Backend,
registers all the endpoint routers, and defines startup events. The routers
include health checks, user queries, craving logs, AI endpoints, and the search endpoint.
"""

from fastapi import FastAPI

# Import routers from the endpoints modules.
from app.api.endpoints.health import router as health_router
from app.api.endpoints.user_queries import router as user_queries_router
from app.api.endpoints.craving_logs import router as craving_logs_router
from app.api.endpoints.ai_endpoints import router as ai_router
from app.api.endpoints.search_cravings import router as search_router

# Create the FastAPI app with metadata.
app = FastAPI(
    title="CRAVE Trinity Backend",
    description="A modular, AI-powered backend for craving analytics",
    version="0.1.0"
)

# Register routers with appropriate URL prefixes.
app.include_router(health_router, prefix="/api/health")
app.include_router(user_queries_router, prefix="/api/cravings")
app.include_router(craving_logs_router, prefix="/api/cravings")
app.include_router(ai_router, prefix="/api")
app.include_router(search_router, prefix="/api/cravings")

# Define a simple root endpoint for a welcome message.
@app.get("/")
def root():
    return {"message": "Welcome to the CRAVE Trinity Backend API"}

# Application startup event: initialize required resources (e.g., database).
@app.on_event("startup")
def on_startup():
    from app.api.dependencies import init_db
    init_db()
    print("Startup complete: Database and other resources initialized.")