# -------------------------------
# Base Image
# -------------------------------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# install gunicorn
RUN pip install gunicorn

# Copy project
COPY . .

# Gunicorn command for Render
CMD gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4

