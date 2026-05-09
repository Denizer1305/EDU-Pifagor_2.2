from __future__ import annotations

import django_filters

from apps.schedule.models import ScheduleCalendar, ScheduleWeekTemplate


class ScheduleCalendarFilter(django_filters.FilterSet):
    starts_on_after = django_filters.DateFilter("starts_on", lookup_expr="gte")
    starts_on_before = django_filters.DateFilter("starts_on", lookup_expr="lte")
    ends_on_after = django_filters.DateFilter("ends_on", lookup_expr="gte")
    ends_on_before = django_filters.DateFilter("ends_on", lookup_expr="lte")

    class Meta:
        model = ScheduleCalendar
        fields = {
            "organization": ["exact"],
            "academic_year": ["exact"],
            "education_period": ["exact"],
            "calendar_type": ["exact"],
            "is_active": ["exact"],
        }


class ScheduleWeekTemplateFilter(django_filters.FilterSet):
    class Meta:
        model = ScheduleWeekTemplate
        fields = {
            "organization": ["exact"],
            "academic_year": ["exact"],
            "education_period": ["exact"],
            "week_type": ["exact"],
            "is_default": ["exact"],
            "is_active": ["exact"],
        }
