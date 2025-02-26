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

# Use a lightweight Python 3.11 base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and force unbuffered output for logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ------------------------------------------------------------------------------
# 1️⃣ Install System Dependencies
# ------------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ninja-build \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# 2️⃣ Create a Non-Root User for Security
# ------------------------------------------------------------------------------
RUN useradd --create-home appuser
WORKDIR /app
USER appuser

# ------------------------------------------------------------------------------
# 3️⃣ Set Up Virtual Environment & Install Dependencies
# ------------------------------------------------------------------------------
# Create a virtual environment inside /app/venv
RUN python -m venv /app/venv

# Set the virtual environment as default for running commands
ENV PATH="/app/venv/bin:$PATH"

# Copy only requirements first to optimize Docker layer caching
COPY --chown=appuser:appuser requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# 4️⃣ Copy Application Code & Set Up Entrypoint
# ------------------------------------------------------------------------------
COPY --chown=appuser:appuser . .

# Ensure the entrypoint script is executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ------------------------------------------------------------------------------
# 5️⃣ Expose Ports & Start the Application
# ------------------------------------------------------------------------------
EXPOSE 8000

# Run the entrypoint script (which ensures Alembic migrations run before FastAPI)
CMD ["/entrypoint.sh"]
