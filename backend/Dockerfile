FROM python:3.11-slim

WORKDIR /app

# system dependencies for OpenCV (if needed)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать весь код и модель
EXPOSE 8000


RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
  && rm -rf /var/lib/apt/lists/*
