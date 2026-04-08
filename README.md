# EDU-Pifagor

Образовательная платформа **«Пифагор»** — масштабируемая LMS-система для управления образовательным процессом.

## О проекте

Платформа объединяет:
- управление пользователями и ролями;
- образовательные организации, группы и предметы;
- курсы, модули, уроки и учебные материалы;
- задания, тестирование, журнал и посещаемость;
- расписание и напоминания;
- уведомления и обратную связь;
- аналитику по успеваемости и академическим задолженностям.

## Роли пользователей

- Администратор
- Преподаватель
- Студент
- Родитель

## Технологический стек

### Backend
- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery

### Frontend
- Vue 3
- Vite
- Pinia
- Vue Router
- Axios
- SCSS

### Infrastructure
- Docker
- Docker Compose
- Nginx
- Gunicorn

## Структура проекта

```text
edu-pifagor/
├── backend/     # Django + DRF
├── frontend/    # Vue 3 + Vite
├── deploy/      # Docker, Nginx, deploy scripts
├── docs/        # Диаграммы, архитектура, документация
```

## Быстрый старт

### Локально

#### Backend

```bash
cd backend
python -m venv ../.venv
../.venv/Scripts/python -m pip install -r requirements/dev.txt
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Через Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Основные URL в dev-режиме

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

## Документация

- `backend/README.md`
- `frontend/README.md`
- `deploy/README.md`

## Автор

### Быков Денис
- **Роль:** Fullstack-разработчик
- **Контакты:**
  - Email: [denizer1305@yandex.ru](mailto:denizer1305@yandex.ru)
  - Telegram: [@Denizer2036](https://t.me/Denizer2036)
  - VK: [denizer1305](https://vk.com/denizer1305)

Проект разработан в рамках дипломного проектирования в 2026 году.

---
