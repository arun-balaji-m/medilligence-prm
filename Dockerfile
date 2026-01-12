FROM python:3.11-slim

# -------------------------------
# Python runtime optimizations
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# -------------------------------
# System dependencies
# -------------------------------
# ffmpeg        → audio processing (ElevenLabs, LiveKit, Pipecat)
# poppler-utils → pdf to image (pdf2image)
# tesseract-ocr → OCR (pytesseract)
# build-essential → compile python deps
# curl → debugging + API libs
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Python dependencies
# -------------------------------
# Copy only requirements first (Docker cache optimization)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Application code
# -------------------------------
COPY . .

# -------------------------------
# Render port
# -------------------------------
EXPOSE 10000

# -------------------------------
# Start server (Production)
# -------------------------------
# Gunicorn + Uvicorn workers = stable websockets + audio streaming
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:10000"]
