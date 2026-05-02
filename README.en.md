# EDU-Pifagor Educational Platform

[![Backend CI](https://github.com/Denizer1305/EDU-Pifagor_2.2/actions/workflows/backend-ci.yml/badge.svg?branch=dev-backend)](https://github.com/Denizer1305/EDU-Pifagor_2.2/actions/workflows/backend-ci.yml)

**EDU-Pifagor** is a diploma educational platform that combines users, roles, organizations, academic groups, academic periods, courses, assignments, gradebook functionality, feedback, and analytics into a unified digital learning environment.

The project focuses on maintainable backend architecture: domain logic is split into Django apps, write operations live in `services/`, read operations live in `selectors/`, and quality checks are automated with `pre-commit`, `Makefile`, and GitHub Actions.

---

## Contents

- [Stack](#stack)
- [Current Status](#current-status)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Backend Quick Start](#backend-quick-start)
- [Frontend](#frontend)
- [Environment Variables](#environment-variables)
- [Makefile and Quality Checks](#makefile-and-quality-checks)
- [Tests](#tests)
- [Migrations](#migrations)
- [GitHub Actions](#github-actions)
- [Pre-commit](#pre-commit)
- [Security](#security)

---

## Stack

### Backend

- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- django-filter
- drf-spectacular
- django-cors-headers
- WhiteNoise
- Ruff
- pre-commit
- coverage

### Frontend

- Vue.js
- Vite
- JavaScript / TypeScript
- HTML / CSS

### Infrastructure

- Git / GitHub
- GitHub Actions
- Makefile
- Docker / Docker Compose, if containerized local deployment is used

---

## Current Status

The backend currently has a working quality-control infrastructure:

- separate Django settings: `base.py`, `dev.py`, `prod.py`, `testing.py`;
- `Makefile` for local development commands;
- `pre-commit` hooks;
- GitHub Actions backend workflow;
- migration checks through `makemigrations --check --dry-run`;
- backend checks with `ruff check`, `ruff format --check`, `manage.py check`, and the full test suite.

Main backend modules:

- `users` — users, roles, profiles, registration, onboarding;
- `organizations` — organizations, departments, groups, subjects, teacher links;
- `education` — academic years, periods, curricula, workloads, enrollments;
- `course` — courses, modules, lessons, materials, teachers, progress;
- `assignments` — assignments, publications, audiences, answers, reviews, grades;
- `journal` — journal lessons, attendance, grades, summaries, topic progress;
- `feedback` — feedback requests, processing, attachments;
- `common`, `api`, `templates` — shared components, API layer, and templates.

---

## Project Structure

```text
EDU-Pifagor_2.2/
├── .github/
│   └── workflows/
│       └── backend-ci.yml
├── backend/
│   ├── api/
│   ├── apps/
│   │   ├── common/
│   │   ├── users/
│   │   ├── organizations/
│   │   ├── education/
│   │   ├── course/
│   │   ├── assignments/
│   │   ├── journal/
│   │   └── feedback/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── prod.py
│   │   │   └── testing.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── requirements/
│   │   ├── base.txt
│   │   └── dev.txt
│   ├── templates/
│   ├── Makefile
│   ├── manage.py
│   ├── pyproject.toml
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── public/
│   └── src/
├── docs/
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml
├── .env.example
├── README.md
└── README.en.md
```

---

## Requirements

- Python 3.12+
- PostgreSQL 15+
- Redis, if Celery tasks are used
- Node.js 20+ for frontend
- Git
- GNU Make for `Makefile` commands

On Windows, it is often easier to run `make` from WSL. In PowerShell, you can run the underlying `python -m ...` commands directly or install GNU Make separately.

---

## Backend Quick Start

Go to the backend directory:

```bash
cd backend
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements/dev.txt
```

### Linux / macOS / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/dev.txt
```

Create `.env`:

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Apply migrations and start the development server:

```bash
python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev
python manage.py runserver --settings=config.settings.dev
```

The backend will be available at:

```text
http://127.0.0.1:8000/
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend is usually available at:

```text
http://127.0.0.1:5173/
```

A frontend `.env.local` example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

---

## Environment Variables

Django loads environment variables from `backend/.env`.

For local development, use the template:

```bash
cd backend
cp .env.example .env
```

Important variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_TIME_ZONE`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`
- `FEEDBACK_EMAIL`

Never commit a real `.env` file.

---

## Makefile and Quality Checks

Main backend commands are collected in `backend/Makefile`.

```bash
cd backend
make help
```

Common commands:

```bash
make install-dev
make run
make migrate
make makemigrations
make migrations-check
make lint
make lint-fix
make format
make precommit
make check
make test
make test-app APP=apps.users
make test-users
make test-assignments
make test-course
make test-education
make coverage
make coverage-html
make ci
```

If `python` is not available in WSL, run:

```bash
make ci PYTHON=python3
```

---

## Tests

Run the full test suite:

```bash
cd backend
make test
```

Or directly:

```bash
python manage.py test --settings=config.settings.testing
```

App-specific tests:

```bash
make test-users
make test-assignments
make test-course
make test-education
make test-app APP=apps.feedback
```

---

## Migrations

Django migrations should be committed to Git. They describe the database schema history and make deployments reproducible for other developers and CI.

After changing models:

```bash
cd backend
make makemigrations
make migrate
make migrations-check
```

Before committing, run:

```bash
make ci
```

---

## GitHub Actions

The backend workflow is located at:

```text
.github/workflows/backend-ci.yml
```

CI runs:

- dependency installation;
- Ruff lint;
- Ruff format check;
- migration check;
- Django system check;
- backend tests.

Before opening a pull request, run locally:

```bash
cd backend
make ci
```

---

## Pre-commit

Install hooks:

```bash
cd backend
python -m pre_commit install
```

Run all hooks manually:

```bash
python -m pre_commit run --all-files
```

If hooks modify files, run them again and then add the changes:

```bash
git add .
python -m pre_commit run --all-files
git commit -m "chore(backend): update documentation and env examples"
```

---

## Security

Do not commit:

- `.env`;
- real passwords;
- real SMTP passwords;
- tokens;
- secret keys;
- local databases;
- `.venv`;
- `media/`, if it contains user files;
- `staticfiles/`, if it is generated by `collectstatic`.

For public repositories, keep only `.env.example` with safe placeholder values.
