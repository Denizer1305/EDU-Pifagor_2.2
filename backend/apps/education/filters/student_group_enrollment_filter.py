from __future__ import annotations

import django_filters

from apps.education.models import StudentGroupEnrollment


class StudentGroupEnrollmentFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(
        field_name="student_id",
    )
    group = django_filters.NumberFilter(
        field_name="group_id",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    status = django_filters.CharFilter(
        field_name="status",
    )
    is_primary = django_filters.BooleanFilter(
        field_name="is_primary",
    )
    enrollment_date = django_filters.DateFromToRangeFilter(
        field_name="enrollment_date",
    )
    completion_date = django_filters.DateFromToRangeFilter(
        field_name="completion_date",
    )
    journal_number = django_filters.RangeFilter(
        field_name="journal_number",
    )

    class Meta:
        model = StudentGroupEnrollment
        fields = (
            "student",
            "group",
            "academic_year",
            "status",
            "is_primary",
            "enrollment_date",
            "completion_date",
            "journal_number",
        )
