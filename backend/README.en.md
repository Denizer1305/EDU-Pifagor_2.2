# Backend — EDU-Pifagor

The backend of **EDU-Pifagor** is built with **Django + Django REST Framework** and is responsible for API, authentication, users, organizations, academic entities, courses, assignments, gradebook functionality, feedback, and analytics.

---

## Main Features

- user registration and authentication;
- roles and access control;
- student, teacher, and parent profiles;
- organizations, departments, groups, and subjects;
- academic years, periods, curricula, and workloads;
- courses, modules, lessons, materials, and progress;
- assignments, publications, audiences, answers, reviews, and grades;
- journal lessons, attendance, grades, and summaries;
- user feedback and administrative processing;
- testing, linting, formatting, and CI infrastructure.

---

## Stack

- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- django-filter
- drf-spectacular
- django-cors-headers
- Pillow
- WhiteNoise
- Ruff
- pre-commit
- coverage

---

## Backend Structure

```text
backend/
├── api/
├── apps/
│   ├── common/
│   ├── users/
│   ├── organizations/
│   ├── education/
│   ├── course/
│   ├── assignments/
│   ├── journal/
│   └── feedback/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── testing.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── templates/
├── Makefile
├── manage.py
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Django Settings

The project uses separate settings modules:

| Settings module | Purpose |
|---|---|
| `config.settings.dev` | local development |
| `config.settings.testing` | tests and CI |
| `config.settings.prod` | production |

By default, the `Makefile` uses:

```makefile
DJANGO_SETTINGS ?= config.settings.dev
TEST_SETTINGS ?= config.settings.testing
```

---

## Quick Start

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements/dev.txt
Copy-Item .env.example .env
python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev
python manage.py runserver --settings=config.settings.dev
```

### Linux / macOS / WSL

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/dev.txt
cp .env.example .env
python3 manage.py migrate --settings=config.settings.dev
python3 manage.py createsuperuser --settings=config.settings.dev
python3 manage.py runserver --settings=config.settings.dev
```

---

## Environment Variables

Django loads environment variables from:

```text
backend/.env
```

Create it from the template:

```bash
cp .env.example .env
```

Minimum required variables for PostgreSQL mode:

```env
DJANGO_SECRET_KEY=change-me
POSTGRES_DB=edu_pifagor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
```

For real development, use the full `backend/.env.example` file.

---

## Makefile

Show all commands:

```bash
make help
```

Common commands:

```bash
make install-dev
make run
make shell
make createsuperuser
make makemigrations
make migrations-check
make migrate
make showmigrations
make collectstatic
make lint
make lint-fix
make format
make precommit
make check
make test
make test-keepdb
make test-app APP=apps.users
make coverage
make coverage-html
make clean
make ci
```

In WSL, pass Python explicitly if needed:

```bash
make ci PYTHON=python3
```

---

## Quality Checks

Full local check suite:

```bash
make ci
```

It runs:

```bash
python -m ruff check .
python -m ruff format . --check
python manage.py makemigrations --check --dry-run --settings=config.settings.testing
python manage.py check --settings=config.settings.testing
python manage.py test --settings=config.settings.testing
```

---

## Tests

Run all tests:

```bash
make test
```

Run app-specific tests:

```bash
make test-users
make test-assignments
make test-course
make test-education
make test-app APP=apps.feedback
```

Run directly without Makefile:

```bash
python manage.py test --settings=config.settings.testing
```

---

## Migrations

Migrations must be committed to Git.

After changing models:

```bash
make makemigrations
make migrate
make migrations-check
```

Check that no migrations are missing:

```bash
python manage.py makemigrations --check --dry-run --settings=config.settings.testing
```

---

## Pre-commit

Install hooks:

```bash
python -m pre_commit install
```

Run hooks:

```bash
python -m pre_commit run --all-files
```

If hooks modify files, run them again and add the changes:

```bash
git add .
python -m pre_commit run --all-files
```

---

## Architectural Rules

- models describe data structure and constraints;
- `services/` contains business operations and state changes;
- `selectors/` contains read queries and queryset preparation;
- `serializers/` handle API representation and input validation;
- `views/` should stay thin and avoid complex business logic;
- migrations are committed;
- `.env` is not committed;
- `make ci` is run before pull requests.

---

## Useful Local URLs

```text
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/api/
```

If drf-spectacular routes are enabled, API docs are usually available at:

```text
http://127.0.0.1:8000/api/schema/
http://127.0.0.1:8000/api/docs/
```
