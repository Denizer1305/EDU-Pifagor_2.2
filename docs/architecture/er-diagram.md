# ER Diagram

## Назначение

Этот файл фиксирует итоговую ER-модель платформы **«Пифагор»** и служит текстовой опорой для визуальной диаграммы.

## Ключевые домены

### Пользователи и роли
- User
- Role
- UserRole
- Profile
- TeacherProfile
- StudentProfile
- ParentProfile
- ParentStudent

### Организации и учебная структура
- EducationOrganization
- EducationOrganizationType
- EducationForm
- SubjectCategory
- Subject
- Group
- GroupStudent
- AcademicYear
- AcademicPeriod
- TeachingAssignment

### Курсы и контент
- Course
- CourseModule
- Lesson
- LessonImage
- Material
- CourseMaterial
- LessonMaterial

### Оценивание
- Assignment
- AssignmentSubmission
- SubmissionFile
- AssignmentReview
- GradebookEntry
- Test
- TestQuestion
- TestOption
- TestAttempt
- TestAnswer

### Расписание и уведомления
- ScheduleEvent
- Notification
- EmailLog

### Обратная связь
- Feedback
- FeedbackAttachment

## Ключевые правила

- один курс принадлежит одному преподавателю;
- академическое назначение строится через `TeachingAssignment`;
- аналитика не хранится в агрегатных таблицах на старте;
- календарь строится на базе `ScheduleEvent`;
- доступ студентов к курсам определяется через группы и назначения.

## Статус

Актуализировать после каждого значимого изменения БД или правил доступа.
