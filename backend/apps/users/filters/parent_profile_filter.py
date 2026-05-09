from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.filters.common import _has_model_field
from apps.users.models import ParentProfile


class ParentProfileFilter(django_filters.FilterSet):
    """Фильтр профилей родителей."""

    q = django_filters.CharFilter(method="filter_q")

    class Meta:
        model = ParentProfile
        fields = ()

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        q_obj = (
            Q(user__email__icontains=value)
            | Q(user__profile__last_name__icontains=value)
            | Q(user__profile__first_name__icontains=value)
            | Q(user__profile__patronymic__icontains=value)
        )

        if _has_model_field(ParentProfile, "work_place"):
            q_obj |= Q(work_place__icontains=value)

        return queryset.filter(q_obj).distinct()
