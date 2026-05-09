from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import CalendarType
from apps.schedule.models import ScheduleCalendar


def _normalize_calendar_text(value: str | None) -> str:
    return (value or "").strip()


@transaction.atomic
def create_calendar_period(
    *,
    organization,
    academic_year,
    name: str,
    starts_on: date,
    ends_on: date,
    education_period=None,
    calendar_type: str = CalendarType.REGULAR,
    notes: str = "",
    is_active: bool = True,
) -> ScheduleCalendar:
    """
    Создаёт период календаря расписания.

    Подходит для обычных учебных периодов, каникул, праздников,
    практики, экзаменационной сессии и пользовательских периодов.
    """
    calendar_period = ScheduleCalendar(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
        name=_normalize_calendar_text(name),
        calendar_type=calendar_type,
        starts_on=starts_on,
        ends_on=ends_on,
        notes=_normalize_calendar_text(notes),
        is_active=is_active,
    )

    calendar_period.full_clean()
    calendar_period.save()

    return calendar_period


def mark_holiday(
    *,
    organization,
    academic_year,
    name: str,
    starts_on: date,
    ends_on: date | None = None,
    education_period=None,
    notes: str = "",
) -> ScheduleCalendar:
    """
    Создаёт праздничный период.

    Если ends_on не передан, праздник считается однодневным.
    """
    return create_calendar_period(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
        name=name,
        calendar_type=CalendarType.HOLIDAY,
        starts_on=starts_on,
        ends_on=ends_on or starts_on,
        notes=notes,
    )


def mark_vacation(
    *,
    organization,
    academic_year,
    name: str,
    starts_on: date,
    ends_on: date,
    education_period=None,
    notes: str = "",
) -> ScheduleCalendar:
    """
    Создаёт период каникул.
    """
    return create_calendar_period(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
        name=name,
        calendar_type=CalendarType.VACATION,
        starts_on=starts_on,
        ends_on=ends_on,
        notes=notes,
    )


def mark_practice_period(
    *,
    organization,
    academic_year,
    name: str,
    starts_on: date,
    ends_on: date,
    education_period=None,
    notes: str = "",
) -> ScheduleCalendar:
    """
    Создаёт период практики.

    В СПО это важно для недель, где обычные занятия заменяются
    учебной или производственной практикой.
    """
    return create_calendar_period(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
        name=name,
        calendar_type=CalendarType.PRACTICE,
        starts_on=starts_on,
        ends_on=ends_on,
        notes=notes,
    )


def validate_date_is_working_day(
    *,
    organization,
    academic_year,
    target_date: date,
) -> None:
    """
    Проверяет, можно ли ставить обычное занятие на указанную дату.

    Дата считается нерабочей, если она попадает в активный праздник
    или каникулы. Практика не считается ошибкой сама по себе, потому что
    на неё могут генерироваться отдельные занятия типа practice.
    """
    blocking_period = (
        ScheduleCalendar.objects.filter(
            organization=organization,
            academic_year=academic_year,
            is_active=True,
            starts_on__lte=target_date,
            ends_on__gte=target_date,
            calendar_type__in=(
                CalendarType.HOLIDAY,
                CalendarType.VACATION,
            ),
        )
        .order_by("starts_on")
        .first()
    )

    if blocking_period is not None:
        raise ValidationError(
            {
                "date": _(
                    "На выбранную дату нельзя поставить обычное занятие: %(period)s."
                )
                % {"period": blocking_period.name}
            }
        )
