FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    KMP_DUPLICATE_LIB_OK=TRUE

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

# Create storage directories
RUN mkdir -p uploads outputs models

# Expose standard Hugging Face Space port
EXPOSE 7860

# Run FastAPI backend API
CMD ["sh", "-c", "uvicorn app.api.routes:app --host 0.0.0.0 --port "]
