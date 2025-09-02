# Multi-stage build for Wyoming Parakeet server
FROM nvcr.io/nvidia/l4t-pytorch:r36.2.0-pth2.1-py3 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    git \
    libsndfile1 \
    libsox-dev \
    sox \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e . && \
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install nemo-toolkit[asr] && \
    pip install librosa

# Copy application code
COPY wyoming_parakeet/ ./wyoming_parakeet/
COPY script/ ./script/
COPY README.md ./

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 10300

# Set default model environment variable for Jetson
ENV MODEL_NAME="nvidia/parakeet-tdt-0.6b"
ENV DEVICE="cuda"
ENV PRECISION="float16"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import socket; s = socket.socket(); s.connect(('localhost', 10300)); s.close()" || exit 1

# Default command
CMD ["python", "-m", "wyoming_parakeet", \
     "--model", "${MODEL_NAME}", \
     "--uri", "tcp://0.0.0.0:10300", \
     "--data-dir", "/data", \
     "--download-dir", "/data", \
     "--device", "${DEVICE}", \
     "--precision", "${PRECISION}", \
     "--language", "en"]