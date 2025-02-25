#!/bin/bash
set -e

# Check the MIGRATION_MODE environment variable.
# If it's set to "upgrade", run the full upgrade;
# Otherwise (or if set to "stamp"), stamp the database as head.
if [ "$MIGRATION_MODE" = "upgrade" ]; then
  echo "Running Alembic upgrade head..."
  alembic upgrade head
else
  echo "Stamping the database as head..."
  alembic stamp head
fi

echo "Starting FastAPI..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000