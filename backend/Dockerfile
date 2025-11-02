# Backend Dockerfile for Cloud Run with Selenium (Chromium + Chromedriver)
# Base image
FROM python:3.11-slim

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    DEBIAN_FRONTEND=noninteractive \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PORT=8080

# Install system dependencies, Chromium, and Chromedriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    unzip \
    fonts-liberation \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango1.0-0 \
    libstdc++6 \
    lsb-release \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy and install Python dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port (Cloud Run will set $PORT)
EXPOSE 8080

# Default command: run FastAPI server with uvicorn
# server:app is the ASGI path in backend/server.py
CMD ["bash", "-lc", "uvicorn server:app --host 0.0.0.0 --port ${PORT} --log-level info"]
