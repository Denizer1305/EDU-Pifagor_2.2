from __future__ import annotations

import django_filters

from apps.schedule.models import ScheduleConflict


class ScheduleConflictFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter("date", lookup_expr="gte")
    date_before = django_filters.DateFilter("date", lookup_expr="lte")

    class Meta:
        model = ScheduleConflict
        fields = {
            "organization": ["exact"],
            "conflict_type": ["exact"],
            "severity": ["exact"],
            "status": ["exact"],
            "lesson": ["exact"],
            "pattern": ["exact"],
            "teacher": ["exact"],
            "room": ["exact"],
            "group": ["exact"],
            "date": ["exact"],
        }
