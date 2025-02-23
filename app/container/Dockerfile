# crave_trinity_backend/app/container/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of code
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
