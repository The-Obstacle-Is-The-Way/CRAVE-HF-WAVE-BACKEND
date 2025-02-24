# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for PostgreSQL, Hugging Face, and fastAPI
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    libpq-dev \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . /app/

# Expose the port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]