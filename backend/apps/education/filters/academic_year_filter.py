from __future__ import annotations

import django_filters

from apps.education.models import AcademicYear


class AcademicYearFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    is_current = django_filters.BooleanFilter(
        field_name="is_current",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    start_date = django_filters.DateFromToRangeFilter(
        field_name="start_date",
    )
    end_date = django_filters.DateFromToRangeFilter(
        field_name="end_date",
    )

    class Meta:
        model = AcademicYear
        fields = (
            "name",
            "is_current",
            "is_active",
            "start_date",
            "end_date",
        )
