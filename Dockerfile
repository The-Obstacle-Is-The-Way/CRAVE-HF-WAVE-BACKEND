# Use an appropriate base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install curl and other necessary dependencies
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files
COPY . .

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Command to run your FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
