# Образовательная платформа «Пифагор»

[![Backend CI](https://github.com/Denizer1305/EDU-Pifagor_2.2/actions/workflows/backend-ci.yml/badge.svg?branch=dev-backend)](https://github.com/Denizer1305/EDU-Pifagor_2.2/actions/workflows/backend-ci.yml)

**«Пифагор»** — дипломная образовательная платформа, которая объединяет пользователей, роли, организации, учебные группы, учебные периоды, курсы, задания, журнал, обратную связь и аналитику в единую цифровую образовательную среду.

Проект ориентирован на масштабируемую backend-архитектуру: доменная логика разнесена по Django-приложениям, бизнес-операции вынесены в `services/`, чтение данных — в `selectors/`, проверки качества автоматизированы через `pre-commit`, `Makefile` и GitHub Actions.

---

## Содержание

- [Стек](#стек)
- [Текущий статус](#текущий-статус)
- [Структура проекта](#структура-проекта)
- [Требования](#требования)
- [Быстрый старт backend](#быстрый-старт-backend)
- [Frontend](#frontend)
- [Переменные окружения](#переменные-окружения)
- [Makefile и проверки качества](#makefile-и-проверки-качества)
- [Тесты](#тесты)
- [Миграции](#миграции)
- [GitHub Actions](#github-actions)
- [Pre-commit](#pre-commit)
- [Безопасность](#безопасность)

---

## Стек

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

### Инфраструктура

- Git / GitHub
- GitHub Actions
- Makefile
- Docker / Docker Compose, если используется контейнерный запуск

---

## Текущий статус

На текущем этапе backend уже имеет рабочую инфраструктуру качества:

- настроены отдельные Django settings: `base.py`, `dev.py`, `prod.py`, `testing.py`;
- настроен `Makefile` для локальных команд разработки;
- настроен `pre-commit`;
- настроен GitHub Actions workflow для backend;
- миграции проверяются через `makemigrations --check --dry-run`;
- backend проходит `ruff check`, `ruff format --check`, `manage.py check` и полный набор тестов.

Основные backend-модули:

- `users` — пользователи, роли, профили, регистрация, onboarding;
- `organizations` — организации, отделения, группы, предметы, связи преподавателей;
- `education` — учебные годы, периоды, учебные планы, нагрузки, зачисления;
- `course` — курсы, модули, уроки, материалы, преподаватели, прогресс;
- `assignments` — задания, публикации, аудитории, ответы, проверки, оценки;
- `journal` — уроки журнала, посещаемость, оценки, сводки, прогресс тем;
- `feedback` — обратная связь, обращения, обработка, вложения;
- `common`, `api`, `templates` — общие компоненты, API-слой и шаблоны.

---

## Структура проекта

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

## Требования

- Python 3.12+
- PostgreSQL 15+
- Redis, если используются Celery-задачи
- Node.js 20+ для frontend
- Git
- GNU Make для работы с `Makefile`

На Windows удобнее запускать `make` через WSL. В PowerShell можно запускать команды напрямую через `python -m ...`, либо установить GNU Make отдельно.

---

## Быстрый старт backend

Перейдите в backend:

```bash
cd backend
```

Создайте окружение:

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

Создайте `.env`:

```bash
cp .env.example .env
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Примените миграции и запустите сервер:

```bash
python manage.py migrate --settings=config.settings.dev
python manage.py createsuperuser --settings=config.settings.dev
python manage.py runserver --settings=config.settings.dev
```

Backend будет доступен по адресу:

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

Обычно frontend доступен по адресу:

```text
http://127.0.0.1:5173/
```

Для подключения к backend можно использовать `.env.local` во frontend:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

---

## Переменные окружения

Django загружает переменные из файла `backend/.env`.

Для локального запуска используйте шаблон:

```bash
cd backend
cp .env.example .env
```

Важные переменные:

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

Файл `.env` нельзя коммитить в репозиторий.

---

## Makefile и проверки качества

Все основные backend-команды собраны в `backend/Makefile`.

```bash
cd backend
make help
```

Основные команды:

```bash
make install-dev          # установить dev-зависимости
make run                  # запустить dev-сервер
make migrate              # применить миграции
make makemigrations       # создать миграции
make migrations-check     # проверить, что миграции актуальны
make lint                 # Ruff lint
make lint-fix             # Ruff lint с автоисправлениями
make format               # Ruff format
make precommit            # все pre-commit hooks
make check                # Django system check
make test                 # все тесты
make test-app APP=apps.users
make test-users
make test-assignments
make test-course
make test-education
make coverage
make coverage-html
make ci                   # полный набор проверок как в CI
```

Если в WSL команда `python` недоступна, используйте:

```bash
make ci PYTHON=python3
```

---

## Тесты

Полный запуск тестов:

```bash
cd backend
make test
```

Или напрямую:

```bash
python manage.py test --settings=config.settings.testing
```

Тесты отдельных приложений:

```bash
make test-users
make test-assignments
make test-course
make test-education
make test-app APP=apps.feedback
```

---

## Миграции

Миграции Django должны храниться в Git. Они описывают историю схемы базы данных и нужны для одинакового разворачивания проекта у всех участников и в CI.

После изменения моделей:

```bash
cd backend
make makemigrations
make migrate
make migrations-check
```

Перед коммитом полезно проверить:

```bash
make ci
```

---

## GitHub Actions

Backend workflow находится в:

```text
.github/workflows/backend-ci.yml
```

CI запускает:

- установку Python-зависимостей;
- Ruff lint;
- Ruff format check;
- проверку миграций;
- Django system check;
- тесты backend.

Перед pull request локально запускайте:

```bash
cd backend
make ci
```

---

## Pre-commit

Установка хуков:

```bash
cd backend
python -m pre_commit install
```

Ручной запуск всех хуков:

```bash
python -m pre_commit run --all-files
```

Если hooks исправили файлы, нужно повторить команду и затем добавить изменения в Git:

```bash
git add .
python -m pre_commit run --all-files
git commit -m "chore(backend): update documentation and env examples"
```

---

## Безопасность

Нельзя коммитить:

- `.env`;
- реальные пароли;
- реальные SMTP-пароли;
- токены;
- секретные ключи;
- локальные базы данных;
- `.venv`;
- `media/`, если там пользовательские файлы;
- `staticfiles/`, если это результат `collectstatic`.

Для публичного репозитория используйте только `.env.example` с безопасными placeholder-значениями.
