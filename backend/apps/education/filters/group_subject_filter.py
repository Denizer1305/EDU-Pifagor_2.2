from __future__ import annotations

import django_filters

from apps.education.models import GroupSubject


class GroupSubjectFilter(django_filters.FilterSet):
    group = django_filters.NumberFilter(
        field_name="group_id",
    )
    subject = django_filters.NumberFilter(
        field_name="subject_id",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    period = django_filters.NumberFilter(
        field_name="period_id",
    )
    assessment_type = django_filters.CharFilter(
        field_name="assessment_type",
    )
    is_required = django_filters.BooleanFilter(
        field_name="is_required",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    planned_hours = django_filters.RangeFilter(
        field_name="planned_hours",
    )
    contact_hours = django_filters.RangeFilter(
        field_name="contact_hours",
    )
    independent_hours = django_filters.RangeFilter(
        field_name="independent_hours",
    )

    class Meta:
        model = GroupSubject
        fields = (
            "group",
            "subject",
            "academic_year",
            "period",
            "assessment_type",
            "is_required",
            "is_active",
            "planned_hours",
            "contact_hours",
            "independent_hours",
        )
