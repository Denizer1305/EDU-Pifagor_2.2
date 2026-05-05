from __future__ import annotations

from typing import Any

_counter = 0


def next_number() -> int:
    global _counter
    _counter += 1
    return _counter


def create_schedule_context() -> dict[str, Any]:
    from apps.schedule.tests.factories.calendar import (
        create_academic_year,
        create_education_period,
        create_schedule_calendar,
        create_schedule_week_template,
    )
    from apps.schedule.tests.factories.course import (
        create_course,
        create_course_lesson,
        create_group,
        create_organization,
    )
    from apps.schedule.tests.factories.rooms import create_schedule_room
    from apps.schedule.tests.factories.slots import create_schedule_time_slot
    from apps.schedule.tests.factories.users import create_student, create_teacher

    organization = create_organization()
    academic_year = create_academic_year()
    education_period = create_education_period(academic_year=academic_year)
    teacher = create_teacher()
    student = create_student()
    group = create_group(organization=organization)
    course = create_course(
        organization=organization,
        group=group,
        teacher=teacher,
    )
    course_lesson = create_course_lesson(course=course)
    room = create_schedule_room(organization=organization)
    time_slot = create_schedule_time_slot(organization=organization)
    calendar = create_schedule_calendar(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
    )
    week_template = create_schedule_week_template(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
    )

    return {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "teacher": teacher,
        "student": student,
        "group": group,
        "course": course,
        "course_lesson": course_lesson,
        "room": room,
        "time_slot": time_slot,
        "calendar": calendar,
        "week_template": week_template,
    }
