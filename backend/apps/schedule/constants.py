from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class RoomType(models.TextChoices):
    CLASSROOM = "classroom", _("Учебный кабинет")
    LABORATORY = "laboratory", _("Лаборатория")
    COMPUTER_LAB = "computer_lab", _("Компьютерный класс")
    WORKSHOP = "workshop", _("Мастерская")
    GYM = "gym", _("Спортзал")
    LIBRARY = "library", _("Библиотека")
    LECTURE_HALL = "lecture_hall", _("Лекционная аудитория")
    ONLINE = "online", _("Онлайн")
    OTHER = "other", _("Другое")


class CalendarType(models.TextChoices):
    REGULAR = "regular", _("Обычный учебный период")
    VACATION = "vacation", _("Каникулы")
    HOLIDAY = "holiday", _("Праздник")
    PRACTICE = "practice", _("Практика")
    EXAM_SESSION = "exam_session", _("Экзаменационная сессия")
    CONSULTATION_PERIOD = "consultation_period", _("Период консультаций")
    CUSTOM = "custom", _("Пользовательский период")


class EducationLevel(models.TextChoices):
    SCHOOL = "school", _("Школа")
    SPO = "spo", _("СПО")
    UNIVERSITY = "university", _("Вуз")
    MIXED = "mixed", _("Смешанный формат")


class WeekType(models.TextChoices):
    EVERY = "every", _("Каждая неделя")
    NUMERATOR = "numerator", _("Числитель")
    DENOMINATOR = "denominator", _("Знаменатель")
    CUSTOM = "custom", _("Пользовательская неделя")


class Weekday(models.IntegerChoices):
    MONDAY = 1, _("Понедельник")
    TUESDAY = 2, _("Вторник")
    WEDNESDAY = 3, _("Среда")
    THURSDAY = 4, _("Четверг")
    FRIDAY = 5, _("Пятница")
    SATURDAY = 6, _("Суббота")
    SUNDAY = 7, _("Воскресенье")


class LessonType(models.TextChoices):
    LESSON = "lesson", _("Урок")
    LECTURE = "lecture", _("Лекция")
    SEMINAR = "seminar", _("Семинар")
    PRACTICE = "practice", _("Практическое занятие")
    LAB = "lab", _("Лабораторная работа")
    WORKSHOP = "workshop", _("Мастерская")
    CONSULTATION = "consultation", _("Консультация")
    EXAM = "exam", _("Экзамен")
    CREDIT = "credit", _("Зачёт")
    TEST = "test", _("Контрольная работа")
    CLASS_HOUR = "class_hour", _("Классный час")
    PRACTICE_PERIOD = "practice_period", _("Практика")
    INDEPENDENT_WORK = "independent_work", _("Самостоятельная работа")
    OTHER = "other", _("Другое")


class ScheduleSourceType(models.TextChoices):
    MANUAL = "manual", _("Ручное создание")
    KTP = "ktp", _("КТП")
    COURSE = "course", _("Курс")
    PERSONAL_COURSE = "personal_course", _("Персональный курс")
    PRACTICE = "practice", _("Практика")
    EXAM = "exam", _("Экзамен")
    CONSULTATION = "consultation", _("Консультация")
    REPLACEMENT = "replacement", _("Замена")
    EVENT = "event", _("Событие")


class ScheduleStatus(models.TextChoices):
    DRAFT = "draft", _("Черновик")
    PLANNED = "planned", _("Запланировано")
    PUBLISHED = "published", _("Опубликовано")
    COMPLETED = "completed", _("Проведено")
    CANCELLED = "cancelled", _("Отменено")
    RESCHEDULED = "rescheduled", _("Перенесено")
    REPLACED = "replaced", _("Замена")
    MOVED = "moved", _("Перемещено")
    CONFLICT = "conflict", _("Конфликт")
    ARCHIVED = "archived", _("Архив")


class AudienceType(models.TextChoices):
    GROUP = "group", _("Группа")
    SUBGROUP = "subgroup", _("Подгруппа")
    MULTIPLE_GROUPS = "multiple_groups", _("Несколько групп")
    STREAM = "stream", _("Поток")
    STUDENT = "student", _("Студент")
    COURSE_ENROLLMENT = "course_enrollment", _("Запись на курс")
    OPEN_COURSE = "open_course", _("Открытый курс")


class ScheduleChangeType(models.TextChoices):
    CANCEL = "cancel", _("Отмена")
    RESCHEDULE = "reschedule", _("Перенос")
    REPLACE_TEACHER = "replace_teacher", _("Замена преподавателя")
    CHANGE_ROOM = "change_room", _("Смена аудитории")
    CHANGE_TOPIC = "change_topic", _("Изменение темы")
    PUBLISH = "publish", _("Публикация")
    UNPUBLISH = "unpublish", _("Снятие с публикации")
    LOCK = "lock", _("Блокировка")
    UNLOCK = "unlock", _("Разблокировка")


class ConflictType(models.TextChoices):
    TEACHER_OVERLAP = "teacher_overlap", _("Преподаватель занят")
    ROOM_OVERLAP = "room_overlap", _("Аудитория занята")
    GROUP_OVERLAP = "group_overlap", _("Группа занята")
    STUDENT_OVERLAP = "student_overlap", _("Студент занят")
    INVALID_PERIOD = "invalid_period", _("Некорректный учебный период")
    INACTIVE_TEACHER = "inactive_teacher", _("Неактивный преподаватель")
    INACTIVE_GROUP = "inactive_group", _("Неактивная группа")
    INACTIVE_ROOM = "inactive_room", _("Неактивная аудитория")
    COURSE_LESSON_MISMATCH = "course_lesson_mismatch", _("Несоответствие урока курсу")
    HOURS_OVERFLOW = "hours_overflow", _("Превышение часов")
    OUTSIDE_CALENDAR = "outside_calendar", _("Дата вне учебного календаря")


class ConflictSeverity(models.TextChoices):
    INFO = "info", _("Информация")
    WARNING = "warning", _("Предупреждение")
    ERROR = "error", _("Ошибка")
    CRITICAL = "critical", _("Критическая ошибка")


class ConflictStatus(models.TextChoices):
    OPEN = "open", _("Открыт")
    RESOLVED = "resolved", _("Решён")
    IGNORED = "ignored", _("Проигнорирован")


class BatchStatus(models.TextChoices):
    PENDING = "pending", _("Ожидает")
    RUNNING = "running", _("Выполняется")
    SUCCESS = "success", _("Успешно")
    FAILED = "failed", _("Ошибка")
    PARTIAL = "partial", _("Частично выполнено")


class GenerationSource(models.TextChoices):
    PATTERNS = "patterns", _("Шаблоны")
    KTP = "ktp", _("КТП")
    COURSE = "course", _("Курс")
    MANUAL_IMPORT = "manual_import", _("Ручной импорт")
    PDF_IMPORT = "pdf_import", _("Импорт PDF")
    EXCEL_IMPORT = "excel_import", _("Импорт Excel")


class ImportSourceType(models.TextChoices):
    PDF = "pdf", _("PDF")
    EXCEL = "excel", _("Excel")
    CSV = "csv", _("CSV")
    MANUAL = "manual", _("Ручной ввод")
    OTHER = "other", _("Другое")
