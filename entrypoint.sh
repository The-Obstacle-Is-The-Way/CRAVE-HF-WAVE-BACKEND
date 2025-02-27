#!/bin/bash
set -e

echo "==== ENTRYPOINT: Checking MIGRATION_MODE environment variable ===="

# MIGRATION_MODE can be "upgrade", "stamp", or "skip". Default to "stamp" if not set.
MIGRATION_MODE=${MIGRATION_MODE:-stamp}

if [ "$MIGRATION_MODE" = "upgrade" ]; then
  echo "[Alembic] Running 'upgrade head'..."
  alembic upgrade head || echo "Warning: Alembic upgrade failed (possible no DB connection)."
elif [ "$MIGRATION_MODE" = "stamp" ]; then
  echo "[Alembic] Stamping the DB to 'head'..."
  alembic stamp head || echo "Warning: Alembic stamp failed (possible no DB connection)."
else
  echo "[Alembic] Skipping migrations entirely."
fi

echo "==== Starting FastAPI with Uvicorn on port 8000 ===="
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000