# EDU-Pifagor

**Pifagor Educational Platform** is a scalable LMS system designed to manage the educational process.

## About the Project

The platform brings together:
- user and role management;
- educational organizations, groups, and subjects;
- courses, modules, lessons, and learning materials;
- assignments, testing, gradebook, and attendance;
- scheduling and reminders;
- notifications and feedback;
- analytics for academic performance and overdue students.

## User Roles

- Administrator
- Teacher
- Student
- Parent

## Technology Stack

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

## Project Structure

```text
edu-pifagor/
├── backend/     # Django + DRF
├── frontend/    # Vue 3 + Vite
├── deploy/      # Docker, Nginx, deploy scripts
├── docs/        # Diagrams, architecture, documentation
```

## Quick Start

### Local Setup

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

### With Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Main URLs in Development

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

## Documentation

- `backend/README.md`
- `frontend/README.md`
- `deploy/README.md`

## Author

### Denis Bykov
- **Role:** Fullstack Developer
- **Contacts:**
  - Email: [denizer1305@yandex.ru](mailto:denizer1305@yandex.ru)
  - Telegram: [@Denizer2036](https://t.me/Denizer2036)
  - VK: [denizer1305](https://vk.com/denizer1305)

The project was developed as part of a graduation project in 2026.

---
