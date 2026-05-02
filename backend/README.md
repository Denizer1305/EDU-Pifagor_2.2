# Backend — EDU-Pifagor

Backend-часть платформы **«Пифагор»** реализована на **Django + Django REST Framework** и отвечает за API, авторизацию, пользователей, организации, учебные сущности, курсы, задания, электронный журнал, обратную связь и аналитику.

---

## Основные возможности

- регистрация и авторизация пользователей;
- роли и права доступа;
- профили ученика, преподавателя и родителя;
- организации, отделения, группы и предметы;
- учебные годы, периоды, учебные планы и нагрузки;
- курсы, модули, уроки, материалы и прогресс;
- задания, публикации, аудитории, ответы, проверки и оценки;
- журнал занятий, посещаемость, оценки и сводки;
- обратная связь пользователей и административная обработка обращений;
- инфраструктура тестирования, линтинга, форматирования и CI.

---

## Стек

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

## Структура backend

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

## Django settings

Используются отдельные настройки окружений:

| Settings module | Назначение |
|---|---|
| `config.settings.dev` | локальная разработка |
| `config.settings.testing` | тесты и CI |
| `config.settings.prod` | production |

По умолчанию команды `Makefile` используют:

```makefile
DJANGO_SETTINGS ?= config.settings.dev
TEST_SETTINGS ?= config.settings.testing
```

---

## Быстрый старт

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

## Переменные окружения

Django загружает переменные из файла:

```text
backend/.env
```

Создайте его из шаблона:

```bash
cp .env.example .env
```

Минимально обязательные переменные для PostgreSQL-режима:

```env
DJANGO_SECRET_KEY=change-me
POSTGRES_DB=edu_pifagor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5432
```

Для реальной разработки используйте полный `backend/.env.example`.

---

## Makefile

Посмотреть все команды:

```bash
make help
```

Основные команды:

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

В WSL при необходимости указывайте Python явно:

```bash
make ci PYTHON=python3
```

---

## Проверки качества

Локальный полный набор проверок:

```bash
make ci
```

Он выполняет:

```bash
python -m ruff check .
python -m ruff format . --check
python manage.py makemigrations --check --dry-run --settings=config.settings.testing
python manage.py check --settings=config.settings.testing
python manage.py test --settings=config.settings.testing
```

---

## Тесты

Полный запуск:

```bash
make test
```

Тесты отдельных приложений:

```bash
make test-users
make test-assignments
make test-course
make test-education
make test-app APP=apps.feedback
```

Запуск напрямую без Makefile:

```bash
python manage.py test --settings=config.settings.testing
```

---

## Миграции

Миграции должны храниться в Git.

После изменения моделей:

```bash
make makemigrations
make migrate
make migrations-check
```

Проверка отсутствия незакоммиченных миграций:

```bash
python manage.py makemigrations --check --dry-run --settings=config.settings.testing
```

---

## Pre-commit

Установка:

```bash
python -m pre_commit install
```

Запуск:

```bash
python -m pre_commit run --all-files
```

Если хуки изменили файлы, повторите запуск и добавьте изменения:

```bash
git add .
python -m pre_commit run --all-files
```

---

## Архитектурные правила

- модели описывают структуру данных и ограничения;
- `services/` содержит бизнес-операции и изменения состояния;
- `selectors/` содержит чтение и подготовку queryset;
- `serializers/` отвечают за API-представление и валидацию входа;
- `views/` должны быть тонкими и не содержать сложную бизнес-логику;
- миграции коммитятся;
- `.env` не коммитится;
- перед pull request запускается `make ci`.

---

## Полезные URL при локальном запуске

```text
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/api/
```

Если в проекте включены маршруты drf-spectacular, документация API обычно доступна по адресам вида:

```text
http://127.0.0.1:8000/api/schema/
http://127.0.0.1:8000/api/docs/
```
