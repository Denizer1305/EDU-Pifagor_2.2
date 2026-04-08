FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements /app/backend/requirements
RUN pip install --upgrade pip && pip install -r /app/backend/requirements/dev.txt

COPY backend /app/backend
COPY deploy /app/deploy

RUN chmod +x /app/deploy/docker/backend/entrypoint.sh

EXPOSE 8000
