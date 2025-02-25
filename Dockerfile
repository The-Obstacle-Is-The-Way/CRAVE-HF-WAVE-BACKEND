# Dockerfile
# ------------------------------------------------------------------------------
# A lightweight Docker image for the CRAVE Trinity Backend.
#
# This Dockerfile uses Python 3.11-slim and installs dependencies in two phases:
# 1. Upgrading pip and installing torch explicitly.
# 2. Installing the remainder of the requirements from requirements.txt.
#
# This two-phase approach ensures that xformers (which requires torch to be pre‐installed)
# builds successfully without metadata-generation errors.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    # Prevent Python from writing .pyc files and ensure unbuffered output.
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    # Set the working directory inside the container.
    WORKDIR /app
    
    # Copy the requirements file first to leverage Docker layer caching.
    COPY requirements.txt .
    
    # Phase 1: Upgrade pip and install torch first.
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir torch==2.0.1
    
    # Phase 2: Install the rest of the dependencies.
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy the entire application code into the container.
    COPY . .
    
    # Expose the application port.
    EXPOSE 8000
    
    # Define the command to run the application.
    # "main:app" should match the import path of your FastAPI app instance.
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]