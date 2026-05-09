from __future__ import annotations

from datetime import date

from django.db.models import Q, QuerySet

from apps.schedule.constants import CalendarType
from apps.schedule.models import ScheduleCalendar, ScheduleWeekTemplate


def get_calendar_queryset() -> QuerySet[ScheduleCalendar]:
    return ScheduleCalendar.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
    )


def get_active_calendar_periods(
    *,
    organization_id: int,
    academic_year_id: int | None = None,
    education_period_id: int | None = None,
) -> QuerySet[ScheduleCalendar]:
    queryset = get_calendar_queryset().filter(
        organization_id=organization_id,
        is_active=True,
    )

    if academic_year_id is not None:
        queryset = queryset.filter(academic_year_id=academic_year_id)

    if education_period_id is not None:
        queryset = queryset.filter(education_period_id=education_period_id)

    return queryset


def get_calendar_period_by_id(*, calendar_id: int) -> ScheduleCalendar:
    return get_calendar_queryset().get(id=calendar_id)


def get_calendar_periods_for_date(
    *,
    organization_id: int,
    target_date: date,
    active_only: bool = True,
) -> QuerySet[ScheduleCalendar]:
    queryset = get_calendar_queryset().filter(
        organization_id=organization_id,
        starts_on__lte=target_date,
        ends_on__gte=target_date,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_calendar_periods_for_range(
    *,
    organization_id: int,
    starts_on: date,
    ends_on: date,
    active_only: bool = True,
) -> QuerySet[ScheduleCalendar]:
    queryset = get_calendar_queryset().filter(
        organization_id=organization_id,
        starts_on__lte=ends_on,
        ends_on__gte=starts_on,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_holidays_for_range(
    *,
    organization_id: int,
    starts_on: date,
    ends_on: date,
) -> QuerySet[ScheduleCalendar]:
    return get_calendar_periods_for_range(
        organization_id=organization_id,
        starts_on=starts_on,
        ends_on=ends_on,
    ).filter(calendar_type=CalendarType.HOLIDAY)


def get_vacations_for_range(
    *,
    organization_id: int,
    starts_on: date,
    ends_on: date,
) -> QuerySet[ScheduleCalendar]:
    return get_calendar_periods_for_range(
        organization_id=organization_id,
        starts_on=starts_on,
        ends_on=ends_on,
    ).filter(calendar_type=CalendarType.VACATION)


def get_practice_periods_for_range(
    *,
    organization_id: int,
    starts_on: date,
    ends_on: date,
) -> QuerySet[ScheduleCalendar]:
    return get_calendar_periods_for_range(
        organization_id=organization_id,
        starts_on=starts_on,
        ends_on=ends_on,
    ).filter(calendar_type=CalendarType.PRACTICE)


def is_non_working_date(*, organization_id: int, target_date: date) -> bool:
    return (
        get_calendar_periods_for_date(
            organization_id=organization_id,
            target_date=target_date,
        )
        .filter(
            Q(calendar_type=CalendarType.HOLIDAY)
            | Q(calendar_type=CalendarType.VACATION)
        )
        .exists()
    )


def get_week_template_queryset() -> QuerySet[ScheduleWeekTemplate]:
    return ScheduleWeekTemplate.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
    )


def get_active_week_templates(
    *,
    organization_id: int,
    academic_year_id: int | None = None,
    education_period_id: int | None = None,
) -> QuerySet[ScheduleWeekTemplate]:
    queryset = get_week_template_queryset().filter(
        organization_id=organization_id,
        is_active=True,
    )

    if academic_year_id is not None:
        queryset = queryset.filter(academic_year_id=academic_year_id)

    if education_period_id is not None:
        queryset = queryset.filter(education_period_id=education_period_id)

    return queryset


def get_default_week_template(
    *,
    organization_id: int,
    academic_year_id: int,
    education_period_id: int | None = None,
) -> ScheduleWeekTemplate | None:
    queryset = get_active_week_templates(
        organization_id=organization_id,
        academic_year_id=academic_year_id,
        education_period_id=education_period_id,
    ).filter(is_default=True)

    return queryset.first()
