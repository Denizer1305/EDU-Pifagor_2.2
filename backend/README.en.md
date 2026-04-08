# Backend — EDU-Pifagor

The backend part of **Pifagor Educational Platform** is built with **Django + Django REST Framework** and is responsible for business logic, API, authentication, educational workflows, scheduling, notifications, and analytics.

## Purpose

The backend provides:
- authentication and user management;
- role-based access control;
- educational organizations, groups, and subjects management;
- course creation and maintenance;
- lessons, materials, assignments, and tests management;
- scheduling;
- notifications and email delivery;
- analytics and overdue student reporting.

## Main Stack

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- django-filter
- drf-spectacular
- Pillow
- django-cors-headers

## Suggested Backend Structure

```text
backend/
├── manage.py
├── README.md
├── pyproject.toml
├── .env.example
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   ├── celery_app.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       ├── prod.py
│       └── test.py
├── apps/
│   ├── common/
│   ├── users/
│   ├── organizations/
│   ├── education/
│   ├── courses/
│   ├── content/
│   ├── assignments/
│   ├── testing/
│   ├── schedule/
│   ├── notifications/
│   ├── feedback/
│   └── analytics/
├── api/
├── templates/
│   └── emails/
├── static/
├── media/
├── locale/
├── scripts/
└── tests/
```

## Core Domain Modules

### users
- `User`
- `Role`
- `UserRole`
- `Profile`
- `TeacherProfile`
- `StudentProfile`
- `ParentProfile`
- `ParentStudent`

### organizations
- `EducationOrganization`
- `EducationOrganizationType`
- `EducationForm`
- `SubjectCategory`
- `Subject`

### education
- `Group`
- `GroupStudent`
- `AcademicYear`
- `AcademicPeriod`
- `TeachingAssignment`

### courses
- `Course`
- `CourseModule`
- `Lesson`
- `LessonImage`

### content
- `Material`
- `CourseMaterial`
- `LessonMaterial`

### assignments
- `Assignment`
- `AssignmentSubmission`
- `SubmissionFile`
- `AssignmentReview`
- `GradebookEntry`

### testing
- `Test`
- `TestQuestion`
- `TestOption`
- `TestAttempt`
- `TestAnswer`

### schedule
- `ScheduleEvent`

### notifications
- `Notification`
- `EmailLog`
- background email tasks
- reminders

### feedback
- `Feedback`
- `FeedbackAttachment`

### analytics
- query-based analytics services;
- overdue students;
- academic performance;
- attendance;
- course and group reports.

## Architectural Principles

- one course belongs to one teacher;
- academic logic is centered around `TeachingAssignment`;
- analytics is query-based, without aggregated tables at the initial stage;
- scheduling is built around the universal `ScheduleEvent` entity;
- write logic belongs in `services/`, read logic belongs in `selectors/`.

## Local Run

### 1. Create environment

```bash
python -m venv ../.venv
../.venv/Scripts/python -m pip install -r requirements/dev.txt
```

### 2. Apply migrations

```bash
python manage.py migrate
```

### 3. Start server

```bash
python manage.py runserver 0.0.0.0:8000
```

## Environment Variables

Main settings:
- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `REDIS_HOST`
- `REDIS_PORT`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

See:
- root `.env.example`
- `backend/.env.example`

## Tests and Checks

```bash
python manage.py check
python manage.py test
```

## Recommended Implementation Order

1. users / auth
2. organizations / education
3. courses / content
4. assignments / testing
5. schedule
6. notifications / feedback
7. analytics
