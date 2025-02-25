#!/bin/bash
set -e

echo "Running Alembic migrations..."
# Run migrations; ensure alembic.ini is correctly configured
alembic upgrade head

echo "Starting FastAPI..."
# Start the FastAPI server (adjust the module path if needed)
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000