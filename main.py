# main.py
from fastapi import FastAPI
from app.api.endpoints import health, craving_logs
from app.infrastructure.vector_db.pinecone_client import init_pinecone

def create_app() -> FastAPI:
    app = FastAPI(...)
    app.include_router(health.router)
    app.include_router(craving_logs.router)

    @app.on_event("startup")
    def startup_event():
        init_pinecone()  # only once
        # any other setup

    return app

# main.py
from app.api.endpoints import ai_endpoints

def create_app() -> FastAPI:
    ...
    app.include_router(ai_endpoints.router)
    ...
