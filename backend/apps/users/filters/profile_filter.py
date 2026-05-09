from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.models import Profile


class ProfileFilter(django_filters.FilterSet):
    """Фильтр базовых профилей пользователей."""

    q = django_filters.CharFilter(method="filter_q")
    gender = django_filters.CharFilter(field_name="gender")
    city = django_filters.CharFilter(
        field_name="city",
        lookup_expr="icontains",
    )

    class Meta:
        model = Profile
        fields = (
            "gender",
            "city",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(user__email__icontains=value)
            | Q(last_name__icontains=value)
            | Q(first_name__icontains=value)
            | Q(patronymic__icontains=value)
            | Q(phone__icontains=value)
        ).distinct()
