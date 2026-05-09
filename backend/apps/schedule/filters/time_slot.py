from __future__ import annotations

import django_filters

from apps.schedule.models import ScheduleTimeSlot


class ScheduleTimeSlotFilter(django_filters.FilterSet):
    class Meta:
        model = ScheduleTimeSlot
        fields = {
            "organization": ["exact"],
            "number": ["exact", "gte", "lte"],
            "education_level": ["exact"],
            "is_pair": ["exact"],
            "is_active": ["exact"],
        }
