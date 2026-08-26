# Stage 1: Build the Vite + React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend + Production Server
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies for OpenCV and PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY sample_data/ ./sample_data/
COPY run_server.py .

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create storage directories
RUN mkdir -p uploads outputs models

# Expose standard Hugging Face Space port
EXPOSE 7860

# Run FastAPI serving both API and static frontend
CMD ["uvicorn", "app.api.routes:app", "--host", "0.0.0.0", "--port", "7860"]
