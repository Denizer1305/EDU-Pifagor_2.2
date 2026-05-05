from __future__ import annotations

from datetime import date
from typing import Any

from apps.education.models import AcademicYear, EducationPeriod
from apps.organizations.models import Organization
from apps.schedule.constants import CalendarType, WeekType
from apps.schedule.models import ScheduleCalendar, ScheduleWeekTemplate
from apps.schedule.tests.factories.context import next_number
from apps.schedule.tests.factories.course import create_organization


def _model_field_names(model: type) -> set[str]:
    return {
        field.name
        for field in model._meta.fields
        if not field.auto_created and field.name != "id"
    }


def _clean_kwargs(model: type, kwargs: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = _model_field_names(model)
    return {key: value for key, value in kwargs.items() if key in allowed_fields}


def _set_date_aliases(
    defaults: dict[str, Any],
    *,
    starts_on: date,
    ends_on: date,
) -> None:
    """
    Поддерживает разные варианты названий дат в уже существующих моделях:
    - starts_on / ends_on
    - start_date / end_date
    - date_start / date_end
    """
    defaults.update(
        {
            "starts_on": starts_on,
            "ends_on": ends_on,
            "start_date": starts_on,
            "end_date": ends_on,
            "date_start": starts_on,
            "date_end": ends_on,
        }
    )


def create_academic_year(**kwargs: Any) -> AcademicYear:
    number = next_number()

    defaults: dict[str, Any] = {
        "name": f"2025/2026 тестовый {number}",
        "year": 2025,
        "is_current": False,
        "is_active": True,
    }
    _set_date_aliases(
        defaults,
        starts_on=date(2025, 9, 1),
        ends_on=date(2026, 6, 30),
    )
    defaults.update(kwargs)

    return AcademicYear.objects.create(
        **_clean_kwargs(AcademicYear, defaults),
    )


def create_education_period(**kwargs: Any) -> EducationPeriod:
    number = next_number()

    academic_year = kwargs.pop("academic_year", None) or create_academic_year()

    defaults: dict[str, Any] = {
        "academic_year": academic_year,
        "name": f"1 семестр {number}",
        "number": 1,
        "is_active": True,
    }
    _set_date_aliases(
        defaults,
        starts_on=date(2025, 9, 1),
        ends_on=date(2025, 12, 31),
    )
    defaults.update(kwargs)

    return EducationPeriod.objects.create(
        **_clean_kwargs(EducationPeriod, defaults),
    )


def create_schedule_calendar(**kwargs: Any) -> ScheduleCalendar:
    number = next_number()

    organization: Organization = (
        kwargs.pop("organization", None) or create_organization()
    )
    academic_year = kwargs.pop("academic_year", None) or create_academic_year()
    education_period = kwargs.pop("education_period", None)

    defaults = {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "name": f"Период календаря {number}",
        "calendar_type": CalendarType.REGULAR,
        "starts_on": date(2025, 9, 1),
        "ends_on": date(2025, 9, 1),
        "is_working_day": True,
        "is_active": True,
        "notes": "",
    }
    defaults.update(kwargs)

    return ScheduleCalendar.objects.create(
        **_clean_kwargs(ScheduleCalendar, defaults),
    )


def create_schedule_week_template(**kwargs: Any) -> ScheduleWeekTemplate:
    number = next_number()

    organization: Organization = (
        kwargs.pop("organization", None) or create_organization()
    )
    academic_year = kwargs.pop("academic_year", None) or create_academic_year()
    education_period = kwargs.pop("education_period", None)

    defaults = {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "name": f"Шаблон недели {number}",
        "week_type": WeekType.EVERY,
        "starts_on": date(2025, 9, 1),
        "ends_on": date(2025, 9, 7),
        "is_active": True,
        "notes": "",
    }
    defaults.update(kwargs)

    return ScheduleWeekTemplate.objects.create(
        **_clean_kwargs(ScheduleWeekTemplate, defaults),
    )
