from __future__ import annotations

from datetime import date

from django.db.models import Q, QuerySet

from apps.schedule.constants import ScheduleStatus
from apps.schedule.models import SchedulePattern


def get_pattern_queryset() -> QuerySet[SchedulePattern]:
    return SchedulePattern.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "week_template",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "group_subject",
        "teacher_group_subject",
        "course",
        "course_lesson",
    ).prefetch_related("audiences")


def get_active_patterns(
    *,
    organization_id: int | None = None,
    academic_year_id: int | None = None,
    education_period_id: int | None = None,
) -> QuerySet[SchedulePattern]:
    queryset = get_pattern_queryset().filter(is_active=True)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if academic_year_id is not None:
        queryset = queryset.filter(academic_year_id=academic_year_id)

    if education_period_id is not None:
        queryset = queryset.filter(education_period_id=education_period_id)

    return queryset


def get_published_patterns(
    *,
    organization_id: int,
    academic_year_id: int | None = None,
    education_period_id: int | None = None,
) -> QuerySet[SchedulePattern]:
    return get_active_patterns(
        organization_id=organization_id,
        academic_year_id=academic_year_id,
        education_period_id=education_period_id,
    ).filter(status=ScheduleStatus.PUBLISHED)


def get_pattern_by_id(*, pattern_id: int) -> SchedulePattern:
    return get_pattern_queryset().get(id=pattern_id)


def get_patterns_for_group(
    *,
    group_id: int,
    active_only: bool = True,
) -> QuerySet[SchedulePattern]:
    queryset = get_pattern_queryset().filter(group_id=group_id)

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_patterns_for_teacher(
    *,
    teacher_id: int,
    active_only: bool = True,
) -> QuerySet[SchedulePattern]:
    queryset = get_pattern_queryset().filter(teacher_id=teacher_id)

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_patterns_for_room(
    *,
    room_id: int,
    active_only: bool = True,
) -> QuerySet[SchedulePattern]:
    queryset = get_pattern_queryset().filter(room_id=room_id)

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_patterns_for_course(
    *,
    course_id: int,
    active_only: bool = True,
) -> QuerySet[SchedulePattern]:
    queryset = get_pattern_queryset().filter(course_id=course_id)

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_patterns_for_weekday(
    *,
    organization_id: int,
    weekday: int,
    active_only: bool = True,
) -> QuerySet[SchedulePattern]:
    queryset = get_pattern_queryset().filter(
        organization_id=organization_id,
        weekday=weekday,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_patterns_active_on_date(
    *,
    organization_id: int,
    target_date: date,
    active_only: bool = True,
) -> QuerySet[SchedulePattern]:
    queryset = (
        get_pattern_queryset()
        .filter(
            organization_id=organization_id,
        )
        .filter(
            Q(starts_on__isnull=True) | Q(starts_on__lte=target_date),
            Q(ends_on__isnull=True) | Q(ends_on__gte=target_date),
        )
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset
