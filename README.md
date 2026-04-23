# Образовательная платформа «Пифагор»

**Образовательная платформа «Пифагор»** — образовательная цифровая платформа, объединяющая учебный процесс, управление пользователями, организационную структуру, академические сущности, курсы, задания, тестирование, аналитику и интеллектуального помощника в единой среде.

Проект разрабатывается как **единая цифровая образовательная среда**, а не как набор разрозненных сервисов. На текущем этапе уже реализованы и покрыты тестами базовые доменные модули:

- `users` — пользователи, роли, профили, права доступа;
- `organizations` — организации, подразделения, группы, предметы, преподавательские связи;
- `education` — учебные годы, периоды, зачисления, предметы групп, закрепления преподавателей, учебные планы.

---

# Содержание

- [1. Технологический стек](#1-технологический-стек)
- [2. Структура проекта](#2-структура-проекта)
- [3. Требования для локального запуска](#3-требования-для-локального-запуска)
- [4. Быстрый старт](#4-быстрый-старт)
- [5. Локальный запуск backend без Docker](#5-локальный-запуск-backend-без-docker)
- [6. Локальный запуск frontend](#6-локальный-запуск-frontend)
- [7. Запуск через Docker Compose](#7-запуск-через-docker-compose)
- [8. Запуск Celery](#8-запуск-celery)
- [9. Применение миграций](#9-применение-миграций)
- [10. Создание администратора](#10-создание-администратора)
- [11. Запуск тестов](#11-запуск-тестов)
- [12. Логирование](#12-логирование)

---

# 1. Технологический стек

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

## Инфраструктура
- Docker
- Docker Compose
- Nginx

---

# 2. Структура проекта

Ниже приведена укрупнённая структура проекта:

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

# 3. Требования для локального запуска

Перед запуском проекта желательно иметь установленное ПО:

- **Python 3.12 или выше**
- **Node.js 20+**
- **npm** или **pnpm**
- **PostgreSQL 15+ / 16+ / 17**
- **Redis** — если нужен Celery
- **Git**
- **Docker Desktop** — если запуск через контейнеры

---

# 4. Быстрый старт

Если нужен самый короткий сценарий запуска в локальной среде:

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

Если проект использует Docker:
```bash
docker compose up --build
```

---

# 5. Локальный запуск backend без Docker

## 5.1. Переход в папку backend
```bash
cd backend
```

## 5.2. Создание виртуального окружения

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

## 5.3. Установка зависимостей

Если зависимости разбиты по файлам:
```bash
pip install -r requirements/dev.txt
```

Если в проекте используется единый файл:
```bash
pip install -r requirements.txt
```

## 5.4. Создание `.env`

В корне папки `backend/` должен лежать `.env`.

Пример минимального `.env` для локального запуска:

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

## 5.5. Проверка конфигурации
```bash
python manage.py check
```

Если всё настроено правильно, появится сообщение:

```text
System check identified no issues (0 silenced).
```

## 5.6. Применение миграций
```bash
python manage.py migrate
```

## 5.7. Создание администратора
```bash
python manage.py createsuperuser
```

## 5.8. Запуск dev-сервера
```bash
python manage.py runserver
```

После запуска backend будет доступен по адресу:

```text
http://127.0.0.1:8000/
```

---

# 6. Локальный запуск frontend

## 6.1. Переход в папку frontend
```bash
cd frontend
```

## 6.2. Установка зависимостей
```bash
npm install
```

## 6.3. Создание `.env.local`

Пример:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## 6.4. Запуск dev-сервера
```bash
npm run dev
```

Обычно frontend запускается по адресу:

```text
http://127.0.0.1:5173/
```

---

# 7. Запуск через Docker Compose

Если проект запускается контейнерами, используется `docker-compose.yml`.

## 7.1. Команда запуска
```bash
docker compose up --build
```

## 7.2. Запуск в фоне
```bash
docker compose up -d --build
```

## 7.3. Остановка контейнеров
```bash
docker compose down
```

## 7.4. Полная пересборка
```bash
docker compose down -v
docker compose up --build
```

---

# 8. Запуск Celery

Если используются фоновые задачи:

## 8.1. Запуск worker
```bash
celery -A config worker -l info
```

## 8.2. Запуск beat
```bash
celery -A config beat -l info
```

Если проект запускается через Docker, worker и beat обычно выносятся в отдельные сервисы.

---

# 9. Применение миграций

После изменения моделей нужно выполнить:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# 10. Создание администратора

Команда:

```bash
python manage.py createsuperuser
```

После этого можно зайти в Django admin:

```text
http://127.0.0.1:8000/admin/
```

---

# 11. Запуск тестов

Проект использует отдельные тестовые настройки.

## 11.1. Запуск тестов конкретного приложения

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

## 11.2. Почему используется `config.settings.test`
Тестовая конфигурация позволяет:
- запускать тесты в изолированной базе;
- не использовать production-настройки;
- не ломать локальные рабочие данные.

---

# 12. Логирование

В проекте включено логирование.

Логирование используется для:

- диагностики ошибок;
- мониторинга выполнения задач;
- отслеживания фоновых процессов;
- технического аудита;
- анализа состояния системы при локальной и production-эксплуатации.

В логах желательно фиксировать:

- системные ошибки;
- ошибки валидации;
- исключения при фоновых задачах;
- диагностические отчёты;
- критичные административные действия.

В логах **не должны** храниться:

- пароли;
- токены;
- секретные ключи;
- персональные чувствительные данные в явном виде.

---

# Рекомендуемая последовательность локального запуска

## Вариант 1 — без Docker
1. Установить PostgreSQL.
2. Установить Python-зависимости.
3. Создать `.env`.
4. Выполнить миграции.
5. Создать superuser.
6. Запустить backend.
7. Установить frontend-зависимости.
8. Запустить frontend.
9. При необходимости поднять Redis и Celery.

## Вариант 2 — через Docker
1. Проверить `docker-compose.yml`.
2. Проверить `deploy/docker.env` или локальный env-файл.
3. Выполнить:
```bash
docker compose up --build
```
4. Применить миграции внутри контейнера.
5. Создать администратора.
6. Открыть backend / frontend / Swagger.

---

# Автор проекта

Проект разрабатывается как дипломная образовательная цифровая платформа с архитектурой, ориентированной на масштабирование, поддержку, безопасность и дальнейшее развитие.
