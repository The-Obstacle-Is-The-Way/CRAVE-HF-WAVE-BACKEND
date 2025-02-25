# Dockerfile
# ------------------------------------------------------------------------------
# A lightweight Docker image for the CRAVE Trinity Backend.
#
# This Dockerfile uses Python 3.11-slim and installs dependencies in two phases:
# 1. Install system-level build dependencies required for compiling extensions (e.g., build-essential, ninja-build).
# 2. Upgrade pip, install torch first, then install the rest of the Python dependencies.
#
# Additionally, this Dockerfile copies an entrypoint script that runs Alembic migrations
# before starting the FastAPI application.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    # Prevent Python from writing pyc files and ensure unbuffered output.
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    # Install system-level build dependencies.
    RUN apt-get update && \
        apt-get install -y build-essential ninja-build && \
        apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # Set the working directory inside the container.
    WORKDIR /app
    
    # Copy the requirements file to leverage Docker layer caching.
    COPY requirements.txt .
    
    # Upgrade pip and install torch explicitly.
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir torch==2.0.1
    
    # Install the rest of the dependencies.
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy the entire application code into the container.
    COPY . .
    
    # Copy the entrypoint script and ensure it's executable.
    COPY entrypoint.sh /entrypoint.sh
    RUN chmod +x /entrypoint.sh
    
    # Expose the application port.
    EXPOSE 8000
    
    # Run the entrypoint script.
    CMD ["/entrypoint.sh"]