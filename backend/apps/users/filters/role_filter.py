from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.models import Role, UserRole


class RoleFilter(django_filters.FilterSet):
    """Фильтр ролей."""

    q = django_filters.CharFilter(method="filter_q")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Role
        fields = ("is_active",)

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(code__icontains=value)
            | Q(name__icontains=value)
            | Q(description__icontains=value)
        )


class UserRoleFilter(django_filters.FilterSet):
    """Фильтр связей пользователей и ролей."""

    user_id = django_filters.NumberFilter(field_name="user_id")
    role_id = django_filters.NumberFilter(field_name="role_id")
    role_code = django_filters.CharFilter(
        field_name="role__code",
        lookup_expr="iexact",
    )
    assigned_at_from = django_filters.DateTimeFilter(
        field_name="assigned_at",
        lookup_expr="gte",
    )
    assigned_at_to = django_filters.DateTimeFilter(
        field_name="assigned_at",
        lookup_expr="lte",
    )

    class Meta:
        model = UserRole
        fields = (
            "user_id",
            "role_id",
            "role_code",
        )
