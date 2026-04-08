# API Architecture

## Подход

Backend платформы строится как REST API на базе **Django REST Framework**.

## Основные принципы

- API делится по доменным модулям;
- маршруты именуются последовательно и предсказуемо;
- права доступа проверяются на уровне view, permission classes и сервисов;
- бизнес-логика не выносится во view, а размещается в `services/`;
- сложные выборки и аналитические queryset находятся в `selectors/`.

## Предлагаемые разделы API

### Auth
- login
- logout
- register
- password reset
- current user

### Users
- profiles
- teacher cards
- parent-student links

### Organizations / Education
- organizations
- subjects
- groups
- academic years
- teaching assignments

### Courses
- courses
- modules
- lessons
- materials

### Assignments / Testing
- assignments
- submissions
- reviews
- tests
- attempts

### Schedule
- schedule events
- calendar filters
- reminders

### Notifications
- notifications
- email logs

### Feedback
- feedback messages
- attachments

### Analytics
- overdue students
- performance by group
- course statistics
- attendance reports

## Версионирование

На старте допустимо использовать префикс:
- `/api/`

При росте проекта рекомендуется переход на:
- `/api/v1/`

## Документация API

Планируется использовать:
- `drf-spectacular`
- Swagger UI / ReDoc
