# Backend — EDU-Pifagor

Backend-часть образовательной платформы **«Пифагор»** реализована на **Django + Django REST Framework** и отвечает за бизнес-логику, API, авторизацию, управление учебным процессом, расписанием, уведомлениями и аналитикой.

## Назначение

Backend обеспечивает:
- авторизацию и управление пользователями;
- разграничение ролей и прав доступа;
- работу с образовательными организациями, группами и предметами;
- создание и ведение курсов;
- управление уроками, материалами, заданиями и тестами;
- формирование расписания;
- отправку уведомлений и писем;
- выдачу данных для аналитики и выявления академических задолженностей.

## Основной стек

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

## Предлагаемая структура backend

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

## Ключевые доменные модули

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
- фоновые email-задачи
- напоминания

### feedback
- `Feedback`
- `FeedbackAttachment`

### analytics
- запросы и сервисы аналитики;
- должники;
- успеваемость;
- посещаемость;
- отчёты по группам и курсам.

## Архитектурные принципы

- один курс принадлежит одному преподавателю;
- академическая логика строится через `TeachingAssignment`;
- аналитика рассчитывается запросами к БД, без хранения агрегатных таблиц на старте;
- расписание строится вокруг универсальной сущности `ScheduleEvent`;
- бизнес-логика выносится в `services/`, логика чтения — в `selectors/`.

## Локальный запуск

### 1. Создание окружения

```bash
python -m venv ../.venv
../.venv/Scripts/python -m pip install -r requirements/dev.txt
```

### 2. Применение миграций

```bash
python manage.py migrate
```

### 3. Запуск сервера

```bash
python manage.py runserver
```


## Переменные окружения

Основные настройки:
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

Подробный шаблон смотри в:
- `.env.example` в корне проекта
- `backend/.env.example`

## Тестирование и проверки

```bash
python manage.py check
python manage.py test
```

## Следующий этап разработки

Рекомендуемый порядок реализации:
1. users / auth
2. organizations / education
3. courses / content
4. assignments / testing
5. schedule
6. notifications / feedback
7. analytics
