# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
# and to ensure stdout/stderr are unbuffered.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies:
# - git: required for Hugging Face authentication
# - gcc & g++: required for compiling packages
# - ca-certificates: necessary for HTTPS connections (e.g., for Pinecone)
# - ffmpeg: required for some models that use audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project into the container
COPY . .

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Run the FastAPI application with Uvicorn
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
