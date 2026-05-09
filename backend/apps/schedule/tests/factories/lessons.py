from __future__ import annotations

from datetime import date, time

from apps.schedule.constants import (
    AudienceType,
    LessonType,
    ScheduleSourceType,
    ScheduleStatus,
)
from apps.schedule.models import (
    ScheduledLesson,
    ScheduledLessonAudience,
    ScheduleTimeSlot,
)
from apps.schedule.tests.factories._utils import next_number
from apps.schedule.tests.factories.course import (
    _clean_kwargs,
    create_course,
    create_course_lesson,
    create_group,
    create_group_subject,
)


def _next_number(key: str | None = None) -> int:
    """
    Совместимость с разными версиями next_number:
    - если next_number принимает ключ;
    - если next_number не принимает аргументы.
    """
    try:
        if key is not None:
            return next_number(key)
        return next_number()
    except TypeError:
        return next_number()


def create_schedule_time_slot(**kwargs):
    number = _next_number("schedule_time_slot")

    organization = kwargs.pop("organization", None)
    if organization is None:
        from apps.schedule.tests.factories.course import create_organization

        organization = create_organization()

    starts_at = kwargs.pop("starts_at", time(9, 0))
    ends_at = kwargs.pop("ends_at", time(10, 30))

    defaults = {
        "organization": organization,
        # оставляем несколько вариантов имён — _clean_kwargs сам выбросит лишние
        "name": kwargs.pop("name", f"{number} пара"),
        "title": kwargs.pop("title", f"{number} пара"),
        "number": kwargs.pop("number", number),
        "order": kwargs.pop("order", number),
        "starts_at": starts_at,
        "ends_at": ends_at,
        "start_time": starts_at,
        "end_time": ends_at,
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return ScheduleTimeSlot.objects.create(**_clean_kwargs(ScheduleTimeSlot, defaults))


def create_scheduled_lesson(**kwargs):
    course = kwargs.pop("course", None) or create_course()

    organization = kwargs.pop(
        "organization",
        getattr(course, "organization", None),
    )

    academic_year = kwargs.pop(
        "academic_year",
        getattr(course, "academic_year", None),
    )

    education_period = kwargs.pop(
        "education_period",
        getattr(course, "period", None),
    )

    group_subject = kwargs.pop(
        "group_subject",
        getattr(course, "group_subject", None),
    )

    if group_subject is None:
        group_subject = create_group_subject(
            organization=organization,
            academic_year=academic_year,
            period=education_period,
            subject=getattr(course, "subject", None),
        )

    group = kwargs.pop("group", None) or getattr(group_subject, "group", None)

    subject = kwargs.pop(
        "subject",
        getattr(group_subject, "subject", None) or getattr(course, "subject", None),
    )

    course_lesson = kwargs.pop("course_lesson", None) or create_course_lesson(
        course=course
    )

    time_slot = kwargs.pop("time_slot", None) or create_schedule_time_slot(
        organization=organization
    )

    lesson_date = kwargs.pop("lesson_date", None)
    date_value = kwargs.pop("date", None) or lesson_date

    if date_value is None:
        date_value = getattr(education_period, "start_date", None)

    if date_value is None:
        date_value = getattr(academic_year, "start_date", None)

    if date_value is None:
        date_value = date(2025, 9, 1)

    starts_at = kwargs.pop("starts_at", time_slot.starts_at)
    ends_at = kwargs.pop("ends_at", time_slot.ends_at)

    requested_status = kwargs.pop("status", ScheduleStatus.DRAFT)

    defaults = {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "date": date_value,
        "weekday": kwargs.pop("weekday", date_value.isoweekday()),
        "time_slot": time_slot,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "group": group,
        "subject": subject,
        "group_subject": group_subject,
        "course": course,
        "course_lesson": course_lesson,
        "teacher": kwargs.pop("teacher", None),
        "room": kwargs.pop("room", None),
        "teacher_group_subject": kwargs.pop("teacher_group_subject", None),
        "journal_lesson": kwargs.pop("journal_lesson", None),
        "title": kwargs.pop("title", "Тестовое занятие"),
        "planned_topic": kwargs.pop("planned_topic", "Тестовая тема"),
        "lesson_type": kwargs.pop("lesson_type", LessonType.LESSON),
        "source_type": kwargs.pop("source_type", ScheduleSourceType.MANUAL),
        "status": ScheduleStatus.DRAFT,
        "generated_from_pattern": kwargs.pop("generated_from_pattern", False),
        "generation_batch": kwargs.pop("generation_batch", None),
        "is_locked": kwargs.pop("is_locked", False),
        "is_public": kwargs.pop("is_public", False),
        "created_by": kwargs.pop("created_by", None),
        "updated_by": kwargs.pop("updated_by", None),
        "notes": kwargs.pop("notes", ""),
    }
    defaults.update(kwargs)

    lesson = ScheduledLesson.objects.create(**_clean_kwargs(ScheduledLesson, defaults))

    if requested_status != lesson.status:
        ScheduledLesson.objects.filter(pk=lesson.pk).update(status=requested_status)
        lesson.refresh_from_db()

    return lesson


def create_scheduled_lesson_audience(**kwargs):
    """
    Фабрика ScheduledLessonAudience под фактическую модель:

    В модели поле называется scheduled_lesson, не lesson.
    Но фабрика принимает оба варианта:
    - scheduled_lesson=...
    - lesson=...
    """
    scheduled_lesson = kwargs.pop("scheduled_lesson", None)
    if scheduled_lesson is None:
        scheduled_lesson = kwargs.pop("lesson", None)

    scheduled_lesson = scheduled_lesson or create_scheduled_lesson()

    group = kwargs.pop("group", None)
    if group is None:
        group = getattr(scheduled_lesson, "group", None)

    if group is None:
        group = create_group(
            organization=scheduled_lesson.organization,
            academic_year=scheduled_lesson.academic_year.name,
        )

    defaults = {
        "scheduled_lesson": scheduled_lesson,
        "audience_type": kwargs.pop("audience_type", AudienceType.GROUP),
        "group": group,
        "subgroup_name": kwargs.pop("subgroup_name", ""),
        "student": kwargs.pop("student", None),
        "course_enrollment": kwargs.pop("course_enrollment", None),
        "notes": kwargs.pop("notes", ""),
    }
    defaults.update(kwargs)

    return ScheduledLessonAudience.objects.create(
        **_clean_kwargs(ScheduledLessonAudience, defaults)
    )
