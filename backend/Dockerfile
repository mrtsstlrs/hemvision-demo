FROM python:3.11-slim

WORKDIR /app

# system dependencies for OpenCV (if needed)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать весь код и модель
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
