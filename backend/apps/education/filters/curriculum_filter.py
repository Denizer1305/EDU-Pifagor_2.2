from __future__ import annotations

import django_filters

from apps.education.models import Curriculum, CurriculumItem


class CurriculumFilter(django_filters.FilterSet):
    organization = django_filters.NumberFilter(
        field_name="organization_id",
    )
    department = django_filters.NumberFilter(
        field_name="department_id",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="icontains",
    )
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    total_hours = django_filters.RangeFilter(
        field_name="total_hours",
    )

    class Meta:
        model = Curriculum
        fields = (
            "organization",
            "department",
            "academic_year",
            "code",
            "name",
            "is_active",
            "total_hours",
        )


class CurriculumItemFilter(django_filters.FilterSet):
    curriculum = django_filters.NumberFilter(
        field_name="curriculum_id",
    )
    period = django_filters.NumberFilter(
        field_name="period_id",
    )
    subject = django_filters.NumberFilter(
        field_name="subject_id",
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
    sequence = django_filters.RangeFilter(
        field_name="sequence",
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
        model = CurriculumItem
        fields = (
            "curriculum",
            "period",
            "subject",
            "assessment_type",
            "is_required",
            "is_active",
            "sequence",
            "planned_hours",
            "contact_hours",
            "independent_hours",
        )
