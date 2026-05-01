from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.filters.common import (
    _filter_exact_if_field_exists,
    _filter_gte_if_field_exists,
    _filter_lte_if_field_exists,
    _has_model_field,
)
from apps.users.models import TeacherProfile


class TeacherProfileFilter(django_filters.FilterSet):
    """Фильтр профилей преподавателей."""

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
    is_public_profile = django_filters.BooleanFilter(
        method="filter_is_public_profile",
    )
    experience_years_min = django_filters.NumberFilter(
        method="filter_experience_years_min",
    )
    experience_years_max = django_filters.NumberFilter(
        method="filter_experience_years_max",
    )

    class Meta:
        model = TeacherProfile
        fields = (
            "verification_status",
            "requested_organization_id",
            "requested_department_id",
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

        if _has_model_field(TeacherProfile, "position"):
            q_obj |= Q(position__icontains=value)

        if _has_model_field(TeacherProfile, "employee_code"):
            q_obj |= Q(employee_code__icontains=value)

        if _has_model_field(TeacherProfile, "specialization"):
            q_obj |= Q(specialization__icontains=value)

        if _has_model_field(TeacherProfile, "education"):
            q_obj |= Q(education__icontains=value)

        if _has_model_field(TeacherProfile, "education_info"):
            q_obj |= Q(education_info__icontains=value)

        return queryset.filter(q_obj).distinct()

    def filter_is_public_profile(self, queryset, name, value):
        return _filter_exact_if_field_exists(
            queryset,
            TeacherProfile,
            "is_public_profile",
            value,
        )

    def filter_experience_years_min(self, queryset, name, value):
        return _filter_gte_if_field_exists(
            queryset,
            TeacherProfile,
            "experience_years",
            value,
        )

    def filter_experience_years_max(self, queryset, name, value):
        return _filter_lte_if_field_exists(
            queryset,
            TeacherProfile,
            "experience_years",
            value,
        )
