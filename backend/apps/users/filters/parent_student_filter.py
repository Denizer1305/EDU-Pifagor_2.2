from __future__ import annotations

import django_filters

from apps.users.filters.common import _filter_exact_if_field_exists
from apps.users.models import ParentStudent


class ParentStudentFilter(django_filters.FilterSet):
    """Фильтр связей родитель-студент."""

    parent_id = django_filters.NumberFilter(field_name="parent_id")
    student_id = django_filters.NumberFilter(field_name="student_id")
    relation_type = django_filters.CharFilter(field_name="relation_type")
    status = django_filters.CharFilter(field_name="status")
    is_primary = django_filters.BooleanFilter(method="filter_is_primary")

    class Meta:
        model = ParentStudent
        fields = (
            "parent_id",
            "student_id",
            "relation_type",
            "status",
        )

    def filter_is_primary(self, queryset, name, value):
        return _filter_exact_if_field_exists(
            queryset,
            ParentStudent,
            "is_primary",
            value,
        )
