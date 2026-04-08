# Deploy — EDU-Pifagor

The `deploy/` directory contains infrastructure files and deployment scripts for **Pifagor Educational Platform**.

## Purpose

This directory stores:
- Dockerfiles for backend, frontend, and nginx;
- nginx configurations;
- environment variable templates;
- deployment scripts;
- backup and restore scripts.

## Suggested Structure

```text
deploy/
├── README.md
├── docker/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── frontend/
│   │   └── Dockerfile
│   └── nginx/
│       ├── Dockerfile
│       └── default.conf
├── env/
│   ├── backend.env.example
│   ├── frontend.env.example
│   └── postgres.env.example
├── nginx/
├── scripts/
│   ├── deploy.sh
│   ├── backup.sh
│   └── restore.sh
└── backups/
```

## Containers

The project typically uses:
- `db`
- `redis`
- `backend`
- `frontend`
- `celery_worker`
- `celery_beat`
- `nginx`

## Main Responsibilities

### backend container
- installs Python dependencies;
- runs migrations;
- starts Gunicorn or the development server.

### frontend container
- installs Node.js dependencies;
- runs Vite dev server;
- builds the production version.

### nginx container
- works as a reverse proxy;
- serves static and media files;
- proxies backend and frontend.

### celery
- sends notifications;
- deadline reminders;
- teacher reminders;
- birthday greetings for users.

## Dev and Production

### Local development
Uses:
- `docker-compose.dev.yml`

### Production / staging
Uses:
- `docker-compose.yml`

## Useful Commands

### Start dev environment

```bash
docker compose -f docker-compose.dev.yml up --build
```

### Stop dev environment

```bash
docker compose -f docker-compose.dev.yml down
```

### Rebuild containers

```bash
docker compose -f docker-compose.dev.yml build
```

## Backups

`deploy/scripts/backup.sh` is recommended to handle:
- PostgreSQL dumps;
- media archiving;
- old backup rotation.

## Restore

`deploy/scripts/restore.sh` is recommended to handle:
- database restore;
- media restore.

## Important Note

Files with real secrets and production settings must not be committed to the repository.
Use:
- `.env`
- `deploy/env/*.example`
- server environment variables
