from __future__ import annotations

import django_filters

from apps.education.models import TeacherGroupSubject


class TeacherGroupSubjectFilter(django_filters.FilterSet):
    teacher = django_filters.NumberFilter(
        field_name="teacher_id",
    )
    group_subject = django_filters.NumberFilter(
        field_name="group_subject_id",
    )
    role = django_filters.CharFilter(
        field_name="role",
    )
    is_primary = django_filters.BooleanFilter(
        field_name="is_primary",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    starts_at = django_filters.DateFromToRangeFilter(
        field_name="starts_at",
    )
    ends_at = django_filters.DateFromToRangeFilter(
        field_name="ends_at",
    )
    planned_hours = django_filters.RangeFilter(
        field_name="planned_hours",
    )

    class Meta:
        model = TeacherGroupSubject
        fields = (
            "teacher",
            "group_subject",
            "role",
            "is_primary",
            "is_active",
            "starts_at",
            "ends_at",
            "planned_hours",
        )
