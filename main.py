"""
main.py
--------
Entry point for the CRAVE Trinity Backend.

This file creates the FastAPI application, registers API routers,
and initializes core dependencies (such as the database). The app
is exposed via a standard import string ("main:app") to be used by
uvicorn, ensuring a smooth startup when running in Docker.
"""

from fastapi import FastAPI
from app.api.dependencies import init_db  # Initializes DB connections, etc.

# Import API routers
from app.api.endpoints import health, user_queries, craving_logs, ai_endpoints

# Instantiate the FastAPI app with descriptive metadata.
app = FastAPI(
    title="CRAVE Trinity Backend",
    description="A modular, AI-powered backend for craving analytics",
    version="0.1.0"
)

# Register routers with a common API prefix for consistency.
app.include_router(health.router, prefix="/api")
app.include_router(user_queries.router, prefix="/api")
app.include_router(craving_logs.router, prefix="/api")
app.include_router(ai_endpoints.router, prefix="/api")

@app.get("/")
def root():
    """
    Basic root endpoint to verify that the service is running.
    """
    return {"message": "Welcome to the CRAVE Trinity Backend API"}

@app.on_event("startup")
async def on_startup():
    """
    Application startup event: initialize the database and perform any
    other necessary startup tasks.
    """
    init_db()
    print("Application startup complete – all systems go.")

# Enable running via "python main.py" for local development.
if __name__ == "__main__":
    import uvicorn
    # Uvicorn will load the app using the "main:app" import string.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)