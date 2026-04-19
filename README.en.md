# EDU-Pifagor

**EDU-Pifagor** is a digital educational platform that combines the learning process, user management, organizational structure, academic entities, courses, assignments, testing, analytics, and an intelligent assistant in a single environment.

The project is being developed as a **unified digital educational environment**, not as a set of disconnected services. At the current stage, the following core domain modules have already been implemented and covered with tests:

- `users` — users, roles, profiles, access permissions;
- `organizations` — organizations, departments, groups, subjects, teacher links;
- `education` — academic years, periods, enrollments, group subjects, teacher assignments, curricula.

---

# Contents

- [1. Technology Stack](#1-technology-stack)
- [2. Project Structure](#2-project-structure)
- [3. Local Run Requirements](#3-local-run-requirements)
- [4. Quick Start](#4-quick-start)
- [5. Running Backend Locally Without Docker](#5-running-backend-locally-without-docker)
- [6. Running Frontend Locally](#6-running-frontend-locally)
- [7. Running with Docker Compose](#7-running-with-docker-compose)
- [8. Running Celery](#8-running-celery)
- [9. Applying Migrations](#9-applying-migrations)
- [10. Creating an Administrator](#10-creating-an-administrator)
- [11. Running Tests](#11-running-tests)
- [12. Logging](#12-logging)

---

# 1. Technology Stack

## Backend
- Python 3.12+
- Django
- Django REST Framework
- django-filter
- drf-spectacular
- PostgreSQL
- Celery
- Redis
- Gunicorn
- WhiteNoise

## Frontend
- Vue.js
- Vite
- JavaScript / TypeScript
- HTML / CSS

## Infrastructure
- Docker
- Docker Compose
- Nginx

---

# 2. Project Structure

Below is a simplified project structure:

```text
EDU-Pifagor/
├── backend/
│   ├── apps/
│   │   ├── users/
│   │   ├── organizations/
│   │   ├── education/
│   │   ├── courses/
│   │   ├── content/
│   │   ├── assignments/
│   │   ├── testing/
│   │   ├── schedule/
│   │   ├── notifications/
│   │   ├── feedback/
│   │   └── analytics/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   ├── test.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── api/
│   ├── requirements/
│   ├── manage.py
│   └── .env
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── deploy/
│   ├── docker.env
│   └── ...
├── docker-compose.yml
└── README.md
```

---

# 3. Local Run Requirements

Before running the project locally, it is recommended to have the following software installed:

- **Python 3.12 or later**
- **Node.js 20+**
- **npm** or **pnpm**
- **PostgreSQL 15+ / 16+ / 17**
- **Redis** — if Celery is required
- **Git**
- **Docker Desktop** — if running in containers

---

# 4. Quick Start

If you need the shortest local startup flow:

## Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```

If the project is run with Docker:
```bash
docker compose up --build
```

---

# 5. Running Backend Locally Without Docker

## 5.1. Go to the backend directory
```bash
cd backend
```

## 5.2. Create a virtual environment

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 5.3. Install dependencies

If dependencies are split into files:
```bash
pip install -r requirements/dev.txt
```

If the project uses a single file:
```bash
pip install -r requirements.txt
```

## 5.4. Create `.env`

A `.env` file should be placed in the root of the `backend/` directory.

A minimal example for local run:

```env
DJANGO_SECRET_KEY=dev-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DJANGO_TIME_ZONE=Europe/Moscow

DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=edu_pifagor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOW_CREDENTIALS=True

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

## 5.5. Check configuration
```bash
python manage.py check
```

If the configuration is correct, Django will output:

```text
System check identified no issues (0 silenced).
```

## 5.6. Apply migrations
```bash
python manage.py migrate
```

## 5.7. Create an administrator
```bash
python manage.py createsuperuser
```

## 5.8. Run the development server
```bash
python manage.py runserver
```

After startup, the backend will be available at:

```text
http://127.0.0.1:8000/
```

---

# 6. Running Frontend Locally

## 6.1. Go to the frontend directory
```bash
cd frontend
```

## 6.2. Install dependencies
```bash
npm install
```

## 6.3. Create `.env.local`

Example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## 6.4. Run the development server
```bash
npm run dev
```

The frontend is usually available at:

```text
http://127.0.0.1:5173/
```

---

# 7. Running with Docker Compose

If the project is containerized, `docker-compose.yml` is used.

## 7.1. Start command
```bash
docker compose up --build
```

## 7.2. Start in background
```bash
docker compose up -d --build
```

## 7.3. Stop containers
```bash
docker compose down
```

## 7.4. Full rebuild
```bash
docker compose down -v
docker compose up --build
```

---

# 8. Running Celery

If background tasks are used:

## 8.1. Start worker
```bash
celery -A config worker -l info
```

## 8.2. Start beat
```bash
celery -A config beat -l info
```

If the project is run with Docker, worker and beat are usually started as separate services.

---

# 9. Applying Migrations

After changing models, run:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# 10. Creating an Administrator

Command:

```bash
python manage.py createsuperuser
```

After that, Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

---

# 11. Running Tests

The project uses separate test settings.

## 11.1. Run tests for a specific app

### Users
```bash
python manage.py test apps.users.tests --settings=config.settings.test
```

### Organizations
```bash
python manage.py test apps.organizations.tests --settings=config.settings.test
```

### Education
```bash
python manage.py test apps.education.tests --settings=config.settings.test
```

## 11.2. Why `config.settings.test` is used
The test configuration allows you to:
- run tests in an isolated database;
- avoid using production settings;
- keep local working data safe.

---


# 12. Logging

Logging is enabled in the project.

It is used for:

- error diagnostics;
- monitoring task execution;
- tracking background processes;
- technical audit;
- analyzing system state in local and production environments.

The logs should contain:

- system errors;
- validation errors;
- exceptions in background tasks;
- diagnostic reports;
- critical administrative actions.

The logs must **not** contain:

- passwords;
- tokens;
- secret keys;
- sensitive personal data in plain form.

---


# Recommended Local Startup Sequence

## Option 1 — without Docker
1. Install PostgreSQL.
2. Install Python dependencies.
3. Create `.env`.
4. Apply migrations.
5. Create a superuser.
6. Start backend.
7. Install frontend dependencies.
8. Start frontend.
9. Start Redis and Celery if needed.

## Option 2 — with Docker
1. Check `docker-compose.yml`.
2. Check `deploy/docker.env` or a local env file.
3. Run:
```bash
docker compose up --build
```
4. Apply migrations inside the container.
5. Create an administrator.
6. Open backend / frontend / Swagger.

---

# Project Author

EDU-Pifagor is being developed as a diploma educational platform with an architecture focused on scalability, maintainability, security, and дальнейшее развитие.
