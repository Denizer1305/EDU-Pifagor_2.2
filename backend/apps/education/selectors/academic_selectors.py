from __future__ import annotations

from apps.education.models import AcademicYear, EducationPeriod


def get_academic_years_queryset():
    return AcademicYear.objects.all()


def get_active_academic_years_queryset():
    return AcademicYear.objects.filter(is_active=True)


def get_current_academic_year_queryset():
    return AcademicYear.objects.filter(
        is_active=True,
        is_current=True,
    )


def get_education_periods_queryset():
    return EducationPeriod.objects.select_related(
        "academic_year",
    ).all()


def get_active_education_periods_queryset():
    return EducationPeriod.objects.select_related(
        "academic_year",
    ).filter(is_active=True)


def get_current_education_periods_queryset():
    return EducationPeriod.objects.select_related(
        "academic_year",
    ).filter(
        is_active=True,
        is_current=True,
    )
