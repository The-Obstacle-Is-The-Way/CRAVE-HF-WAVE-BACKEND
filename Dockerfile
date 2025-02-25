# Dockerfile
# ------------------------------------------------------------------------------
# Build a lightweight Docker image for the CRAVE Trinity backend.
# This image uses Python 3.11-slim, installs dependencies, copies the code,
# and launches the FastAPI app via Uvicorn.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    # Prevent Python from writing pyc files to disc and enable unbuffered output.
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1
    
    # Set the working directory inside the container.
    WORKDIR /app
    
    # Copy dependency lists into the container.
    COPY requirements.txt .
    
    # Upgrade pip and install dependencies without cache.
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt
    
    # Copy the entire codebase into the container.
    COPY . .
    
    # Expose port 8000 to be accessible from the host.
    EXPOSE 8000
    
    # Command to run the application.
    # The import string "main:app" must match the app defined in main.py.
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]