from __future__ import annotations

import django_filters

from apps.schedule.models import SchedulePattern, SchedulePatternAudience


class SchedulePatternFilter(django_filters.FilterSet):
    starts_on_after = django_filters.DateFilter("starts_on", lookup_expr="gte")
    starts_on_before = django_filters.DateFilter("starts_on", lookup_expr="lte")
    ends_on_after = django_filters.DateFilter("ends_on", lookup_expr="gte")
    ends_on_before = django_filters.DateFilter("ends_on", lookup_expr="lte")

    class Meta:
        model = SchedulePattern
        fields = {
            "organization": ["exact"],
            "academic_year": ["exact"],
            "education_period": ["exact"],
            "week_template": ["exact"],
            "weekday": ["exact"],
            "time_slot": ["exact"],
            "group": ["exact"],
            "subject": ["exact"],
            "teacher": ["exact"],
            "room": ["exact"],
            "course": ["exact"],
            "course_lesson": ["exact"],
            "lesson_type": ["exact"],
            "source_type": ["exact"],
            "status": ["exact"],
            "is_active": ["exact"],
        }


class SchedulePatternAudienceFilter(django_filters.FilterSet):
    class Meta:
        model = SchedulePatternAudience
        fields = {
            "pattern": ["exact"],
            "audience_type": ["exact"],
            "group": ["exact"],
            "student": ["exact"],
            "course_enrollment": ["exact"],
        }
