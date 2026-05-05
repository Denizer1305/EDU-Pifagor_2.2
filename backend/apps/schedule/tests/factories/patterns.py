from __future__ import annotations

from datetime import time

from apps.schedule.constants import (
    AudienceType,
    LessonType,
    ScheduleSourceType,
    ScheduleStatus,
    Weekday,
)
from apps.schedule.models import SchedulePattern, SchedulePatternAudience
from apps.schedule.tests.factories.calendar import create_schedule_week_template
from apps.schedule.tests.factories.course import (
    create_course,
    create_course_lesson,
    create_group,
)
from apps.schedule.tests.factories.lessons import create_schedule_time_slot


def _clean_kwargs(model_class, values: dict) -> dict:
    model_fields = {field.name for field in model_class._meta.fields}
    return {key: value for key, value in values.items() if key in model_fields}


def create_schedule_pattern(**kwargs):
    course = kwargs.pop("course", None) or create_course()

    organization = kwargs.pop("organization", None) or course.organization
    academic_year = kwargs.pop("academic_year", None) or course.academic_year
    education_period = kwargs.pop("education_period", None) or course.period
    group_subject = kwargs.pop("group_subject", None) or course.group_subject
    subject = kwargs.pop("subject", None) or course.subject

    group = kwargs.pop("group", None)
    if group is None and group_subject is not None:
        group = group_subject.group

    course_lesson = kwargs.pop("course_lesson", None) or create_course_lesson(
        course=course
    )

    week_template = kwargs.pop("week_template", None)
    week_type = kwargs.pop("week_type", None)

    if week_template is None and week_type is not None:
        week_template = create_schedule_week_template(
            academic_year=academic_year,
            week_type=week_type,
        )

    time_slot = kwargs.pop("time_slot", None) or create_schedule_time_slot(
        organization=organization
    )

    starts_at = kwargs.pop("starts_at", None) or getattr(
        time_slot,
        "starts_at",
        time(9, 0),
    )
    ends_at = kwargs.pop("ends_at", None) or getattr(
        time_slot,
        "ends_at",
        time(10, 30),
    )

    starts_on = kwargs.pop("starts_on", None)
    if starts_on is None and education_period is not None:
        starts_on = education_period.start_date
    if starts_on is None and academic_year is not None:
        starts_on = academic_year.start_date

    ends_on = kwargs.pop("ends_on", None)
    if ends_on is None and education_period is not None:
        ends_on = education_period.end_date
    if ends_on is None and academic_year is not None:
        ends_on = academic_year.end_date

    defaults = {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "week_template": week_template,
        "weekday": kwargs.pop("weekday", Weekday.MONDAY),
        "time_slot": time_slot,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "group": group,
        "subject": subject,
        "teacher": kwargs.pop("teacher", None),
        "room": kwargs.pop("room", None),
        "group_subject": group_subject,
        "teacher_group_subject": kwargs.pop("teacher_group_subject", None),
        "course": course,
        "course_lesson": course_lesson,
        "title": kwargs.pop("title", "Тестовый шаблон расписания"),
        "lesson_type": kwargs.pop("lesson_type", LessonType.LESSON),
        "source_type": kwargs.pop("source_type", ScheduleSourceType.MANUAL),
        "status": kwargs.pop("status", ScheduleStatus.DRAFT),
        "starts_on": starts_on,
        "ends_on": ends_on,
        "repeat_rule": kwargs.pop("repeat_rule", ""),
        "priority": kwargs.pop("priority", 100),
        "is_active": kwargs.pop("is_active", True),
        "notes": kwargs.pop("notes", ""),
    }
    defaults.update(kwargs)

    return SchedulePattern.objects.create(**_clean_kwargs(SchedulePattern, defaults))


def create_schedule_pattern_audience(**kwargs):
    pattern = kwargs.pop("pattern", None) or create_schedule_pattern()

    group = kwargs.pop("group", None)
    if group is None:
        group = pattern.group

    if group is None:
        group = create_group(
            organization=pattern.organization,
            academic_year=pattern.academic_year.name,
        )

    defaults = {
        "pattern": pattern,
        "audience_type": kwargs.pop("audience_type", AudienceType.GROUP),
        "group": group,
        "subgroup_name": kwargs.pop("subgroup_name", ""),
        "student": kwargs.pop("student", None),
        "course_enrollment": kwargs.pop("course_enrollment", None),
        "notes": kwargs.pop("notes", ""),
    }
    defaults.update(kwargs)

    return SchedulePatternAudience.objects.create(
        **_clean_kwargs(SchedulePatternAudience, defaults)
    )
