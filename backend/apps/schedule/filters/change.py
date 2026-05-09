from __future__ import annotations

import django_filters

from apps.schedule.models import ScheduleChange


class ScheduleChangeFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter("created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter("created_at", lookup_expr="lte")

    class Meta:
        model = ScheduleChange
        fields = {
            "scheduled_lesson": ["exact"],
            "change_type": ["exact"],
            "old_date": ["exact"],
            "new_date": ["exact"],
            "old_room": ["exact"],
            "new_room": ["exact"],
            "old_teacher": ["exact"],
            "new_teacher": ["exact"],
            "changed_by": ["exact"],
        }
