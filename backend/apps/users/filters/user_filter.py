from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.filters.common import _filter_exact_if_field_exists
from apps.users.models import User


class UserFilter(django_filters.FilterSet):
    """Фильтр пользователей."""

    q = django_filters.CharFilter(method="filter_q")
    registration_type = django_filters.CharFilter(field_name="registration_type")
    onboarding_status = django_filters.CharFilter(field_name="onboarding_status")
    is_email_verified = django_filters.BooleanFilter(method="filter_is_email_verified")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_staff = django_filters.BooleanFilter(field_name="is_staff")
    is_superuser = django_filters.BooleanFilter(field_name="is_superuser")

    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = User
        fields = (
            "registration_type",
            "onboarding_status",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(email__icontains=value)
            | Q(profile__last_name__icontains=value)
            | Q(profile__first_name__icontains=value)
            | Q(profile__patronymic__icontains=value)
        ).distinct()

    def filter_is_email_verified(self, queryset, name, value):
        return _filter_exact_if_field_exists(
            queryset,
            User,
            "is_email_verified",
            value,
        )

    # Backward compatibility: старое имя метода было с опечаткой.
    def filter_is_email_verify(self, queryset, name, value):
        return self.filter_is_email_verified(queryset, name, value)
