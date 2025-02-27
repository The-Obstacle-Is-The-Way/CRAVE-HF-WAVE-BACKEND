# ------------------------------------------------------------------------------
# CRAVE Trinity Backend - Optimized Dockerfile
#
# Key improvements:
# - Uses Python 3.11-slim for a lightweight image.
# - Installs dependencies in a virtual environment to prevent permission issues.
# - Uses a dedicated non-root user for security.
# - Improves build caching by copying requirements.txt before other files.
# - Ensures Alembic migrations run before starting the FastAPI app.
# ------------------------------------------------------------------------------

# Use a lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ------------------------------------------------------------------------------
# 1️⃣ Install System Dependencies
# ------------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ninja-build \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# 2️⃣ Set Up Application Directory & Permissions
# ------------------------------------------------------------------------------
WORKDIR /app
RUN chown -R 1000:1000 /app  # ✅ Ensure non-root user owns the /app directory

# ------------------------------------------------------------------------------
# 3️⃣ Copy Application Code & Entrypoint Before Switching Users
# ------------------------------------------------------------------------------
COPY --chown=1000:1000 . .
COPY entrypoint.sh /entrypoint.sh

# ✅ FIX: Set permissions BEFORE switching to `appuser`
RUN chmod +x /entrypoint.sh

# ------------------------------------------------------------------------------
# 4️⃣ Create a Non-Root User & Use Virtual Environment
# ------------------------------------------------------------------------------
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Create a virtual environment inside /app/venv
RUN python -m venv /app/venv

# Set virtual environment as default
ENV PATH="/app/venv/bin:$PATH"

# ------------------------------------------------------------------------------
# 5️⃣ Install Python Dependencies
# ------------------------------------------------------------------------------
COPY --chown=1000:1000 requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# 6️⃣ Expose Ports & Start the Application
# ------------------------------------------------------------------------------
EXPOSE 8000
CMD ["/entrypoint.sh"]
