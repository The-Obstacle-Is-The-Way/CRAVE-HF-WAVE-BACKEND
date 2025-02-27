# ─────────────────────────────────────────────────────────────────────────────
# FILE: Dockerfile
#
# Purpose:
#   - Build a single Docker image that HF Spaces can run.
#   - Installs dependencies, sets up non-root user, and runs entrypoint.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Don’t create .pyc files, and flush stdout immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user for best practice
RUN useradd --create-home --uid 1000 appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ninja-build \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up a working dir, copy code
WORKDIR /app
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Create a virtual environment inside /app/venv
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Make sure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

# Expose the FastAPI port
EXPOSE 8000

# Finally, run your entrypoint script
CMD ["/app/entrypoint.sh"]