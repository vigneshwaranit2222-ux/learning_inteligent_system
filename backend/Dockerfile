# Backend Dockerfile for Python 3.11 FastAPI
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy codebase
COPY backend /app/backend
COPY ai_engine /app/ai_engine
COPY data /app/data
COPY scripts /app/scripts

ENV PYTHONPATH="/app/backend:/app"
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
