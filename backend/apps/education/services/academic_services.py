from __future__ import annotations

from django.db import transaction

from apps.education.models import AcademicYear, EducationPeriod


def _normalize_str(value):
    return value.strip() if isinstance(value, str) else value


@transaction.atomic
def create_academic_year(
    *,
    name: str,
    start_date,
    end_date,
    description: str = "",
    is_current: bool = False,
    is_active: bool = True,
) -> AcademicYear:
    if is_current:
        AcademicYear.objects.filter(is_current=True).update(is_current=False)

    academic_year = AcademicYear(
        name=_normalize_str(name),
        start_date=start_date,
        end_date=end_date,
        description=_normalize_str(description),
        is_current=is_current,
        is_active=is_active,
    )
    academic_year.full_clean()
    academic_year.save()
    return academic_year


@transaction.atomic
def update_academic_year(
    *,
    academic_year: AcademicYear,
    **validated_data,
) -> AcademicYear:
    is_current = validated_data.get("is_current", academic_year.is_current)

    if is_current:
        AcademicYear.objects.exclude(pk=academic_year.pk).filter(
            is_current=True,
        ).update(is_current=False)

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = _normalize_str(value)
        setattr(academic_year, field, value)

    academic_year.full_clean()
    academic_year.save()
    return academic_year


@transaction.atomic
def create_education_period(
    *,
    academic_year: AcademicYear,
    name: str,
    code: str,
    period_type: str = EducationPeriod.PeriodTypeChoices.SEMESTER,
    sequence: int = 1,
    start_date=None,
    end_date=None,
    description: str = "",
    is_current: bool = False,
    is_active: bool = True,
) -> EducationPeriod:
    if is_current:
        EducationPeriod.objects.filter(
            academic_year=academic_year,
            is_current=True,
        ).update(is_current=False)

    period = EducationPeriod(
        academic_year=academic_year,
        name=_normalize_str(name),
        code=_normalize_str(code),
        period_type=period_type,
        sequence=sequence,
        start_date=start_date,
        end_date=end_date,
        description=_normalize_str(description),
        is_current=is_current,
        is_active=is_active,
    )
    period.full_clean()
    period.save()
    return period


@transaction.atomic
def update_education_period(
    *,
    period: EducationPeriod,
    **validated_data,
) -> EducationPeriod:
    target_academic_year = validated_data.get("academic_year", period.academic_year)
    is_current = validated_data.get("is_current", period.is_current)

    if is_current:
        EducationPeriod.objects.exclude(pk=period.pk).filter(
            academic_year=target_academic_year,
            is_current=True,
        ).update(is_current=False)

    for field, value in validated_data.items():
        if isinstance(value, str):
            value = _normalize_str(value)
        setattr(period, field, value)

    period.full_clean()
    period.save()
    return period
