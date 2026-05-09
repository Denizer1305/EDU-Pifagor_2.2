from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.schedule.models import ScheduleRoom


class ScheduleRoomFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = ScheduleRoom
        fields = {
            "organization": ["exact"],
            "department": ["exact"],
            "room_type": ["exact"],
            "building": ["exact", "icontains"],
            "floor": ["exact"],
            "is_active": ["exact"],
        }

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(number__icontains=value))
