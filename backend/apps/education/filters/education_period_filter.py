from __future__ import annotations

import django_filters

from apps.education.models import EducationPeriod


class EducationPeriodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="icontains",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    period_type = django_filters.CharFilter(
        field_name="period_type",
    )
    sequence = django_filters.RangeFilter(
        field_name="sequence",
    )
    is_current = django_filters.BooleanFilter(
        field_name="is_current",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )

    class Meta:
        model = EducationPeriod
        fields = (
            "name",
            "code",
            "academic_year",
            "period_type",
            "sequence",
            "is_current",
            "is_active",
        )
