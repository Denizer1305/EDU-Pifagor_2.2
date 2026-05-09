from __future__ import annotations

from datetime import date

from django.db.models import QuerySet

from apps.schedule.constants import ScheduleStatus
from apps.schedule.models import ScheduledLesson


def get_lesson_queryset() -> QuerySet[ScheduledLesson]:
    return ScheduledLesson.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "pattern",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "group_subject",
        "teacher_group_subject",
        "course",
        "course_lesson",
        "journal_lesson",
        "generation_batch",
        "created_by",
        "updated_by",
    ).prefetch_related("audiences")


def get_lesson_by_id(*, lesson_id: int) -> ScheduledLesson:
    return get_lesson_queryset().get(id=lesson_id)


def get_lessons_for_organization(
    *,
    organization_id: int,
    academic_year_id: int | None = None,
    education_period_id: int | None = None,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(organization_id=organization_id)

    if academic_year_id is not None:
        queryset = queryset.filter(academic_year_id=academic_year_id)

    if education_period_id is not None:
        queryset = queryset.filter(education_period_id=education_period_id)

    return queryset


def get_lessons_for_date(
    *,
    organization_id: int,
    target_date: date,
    public_only: bool = False,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(
        organization_id=organization_id,
        date=target_date,
    )

    if public_only:
        queryset = queryset.filter(is_public=True)

    return queryset


def get_lessons_for_period(
    *,
    organization_id: int,
    starts_on: date,
    ends_on: date,
    public_only: bool = False,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(
        organization_id=organization_id,
        date__range=(starts_on, ends_on),
    )

    if public_only:
        queryset = queryset.filter(is_public=True)

    return queryset


def get_lessons_for_group(
    *,
    group_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    public_only: bool = False,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(group_id=group_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if public_only:
        queryset = queryset.filter(is_public=True)

    return queryset


def get_lessons_for_teacher(
    *,
    teacher_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    public_only: bool = False,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(teacher_id=teacher_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if public_only:
        queryset = queryset.filter(is_public=True)

    return queryset


def get_lessons_for_room(
    *,
    room_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    public_only: bool = False,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(room_id=room_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if public_only:
        queryset = queryset.filter(is_public=True)

    return queryset


def get_lessons_for_course(
    *,
    course_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    public_only: bool = False,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(course_id=course_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if public_only:
        queryset = queryset.filter(is_public=True)

    return queryset


def get_published_lessons(
    *,
    organization_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(
        organization_id=organization_id,
        status=ScheduleStatus.PUBLISHED,
        is_public=True,
    )

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    return queryset


def get_locked_lessons(
    *,
    organization_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> QuerySet[ScheduledLesson]:
    queryset = get_lesson_queryset().filter(
        organization_id=organization_id,
        is_locked=True,
    )

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    return queryset
