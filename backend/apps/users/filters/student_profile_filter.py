from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.filters.common import (
    _filter_exact_if_field_exists,
    _has_model_field,
)
from apps.users.models import StudentProfile


class StudentProfileFilter(django_filters.FilterSet):
    """Фильтр профилей студентов."""

    q = django_filters.CharFilter(method="filter_q")
    verification_status = django_filters.CharFilter(
        field_name="verification_status",
    )
    requested_organization_id = django_filters.NumberFilter(
        field_name="requested_organization_id",
    )
    requested_department_id = django_filters.NumberFilter(
        field_name="requested_department_id",
    )
    requested_group_id = django_filters.NumberFilter(
        field_name="requested_group_id",
    )
    admission_year = django_filters.NumberFilter(method="filter_admission_year")
    graduation_year = django_filters.NumberFilter(method="filter_graduation_year")

    class Meta:
        model = StudentProfile
        fields = (
            "verification_status",
            "requested_organization_id",
            "requested_department_id",
            "requested_group_id",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        q_obj = (
            Q(user__email__icontains=value)
            | Q(user__profile__last_name__icontains=value)
            | Q(user__profile__first_name__icontains=value)
        )

        if _has_model_field(StudentProfile, "student_code"):
            q_obj |= Q(student_code__icontains=value)

        if _has_model_field(StudentProfile, "submitted_group_code"):
            q_obj |= Q(submitted_group_code__icontains=value)

        return queryset.filter(q_obj).distinct()

    def filter_admission_year(self, queryset, name, value):
        return _filter_exact_if_field_exists(
            queryset,
            StudentProfile,
            "admission_year",
            value,
        )

    def filter_graduation_year(self, queryset, name, value):
        return _filter_exact_if_field_exists(
            queryset,
            StudentProfile,
            "graduation_year",
            value,
        )
