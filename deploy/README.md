# Deploy — EDU-Pifagor

Папка `deploy/` содержит инфраструктурные файлы и сценарии развертывания платформы **«Пифагор»**.

## Назначение

Здесь располагаются:
- Dockerfile для backend, frontend и nginx;
- конфигурации nginx;
- шаблоны переменных окружения;
- скрипты развертывания;
- скрипты резервного копирования и восстановления.

## Предлагаемая структура

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

## Контейнеры

Обычно в проекте используются:
- `db`
- `redis`
- `backend`
- `frontend`
- `celery_worker`
- `celery_beat`
- `nginx`

## Основные задачи

### backend container
- установка Python-зависимостей;
- запуск миграций;
- запуск Gunicorn или dev-сервера.

### frontend container
- установка Node.js-зависимостей;
- запуск Vite dev server;
- сборка production-версии.

### nginx container
- reverse proxy;
- отдача статики и медиа;
- проксирование backend и frontend.

### celery
- отправка уведомлений;
- напоминания о дедлайнах;
- напоминания преподавателям;
- поздравления пользователей с днём рождения.

## Dev и Production

### Для локальной разработки
Используется:
- `docker-compose.dev.yml`

### Для production / staging
Используется:
- `docker-compose.yml`

## Полезные сценарии

### Поднять dev-окружение

```bash
docker compose -f docker-compose.dev.yml up --build
```

### Остановить dev-окружение

```bash
docker compose -f docker-compose.dev.yml down
```

### Пересобрать контейнеры

```bash
docker compose -f docker-compose.dev.yml build
```

## Резервные копии

В `deploy/scripts/backup.sh` рекомендуется реализовать:
- дамп PostgreSQL;
- архивирование media;
- ротацию старых резервных копий.

## Восстановление

В `deploy/scripts/restore.sh` рекомендуется реализовать:
- восстановление базы данных;
- восстановление media-файлов.

## Важное замечание

Файлы с реальными секретами и production-настройками не должны попадать в репозиторий.
Используй:
- `.env`
- `deploy/env/*.example`
- переменные окружения сервера
