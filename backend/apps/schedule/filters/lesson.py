from __future__ import annotations

import django_filters

from apps.schedule.models import ScheduledLesson, ScheduledLessonAudience


class ScheduledLessonFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter("date", lookup_expr="gte")
    date_before = django_filters.DateFilter("date", lookup_expr="lte")

    class Meta:
        model = ScheduledLesson
        fields = {
            "organization": ["exact"],
            "academic_year": ["exact"],
            "education_period": ["exact"],
            "pattern": ["exact"],
            "date": ["exact"],
            "weekday": ["exact"],
            "time_slot": ["exact"],
            "group": ["exact"],
            "subject": ["exact"],
            "teacher": ["exact"],
            "room": ["exact"],
            "course": ["exact"],
            "course_lesson": ["exact"],
            "journal_lesson": ["exact"],
            "lesson_type": ["exact"],
            "source_type": ["exact"],
            "status": ["exact"],
            "is_locked": ["exact"],
            "is_public": ["exact"],
        }


class ScheduledLessonAudienceFilter(django_filters.FilterSet):
    class Meta:
        model = ScheduledLessonAudience
        fields = {
            "scheduled_lesson": ["exact"],
            "audience_type": ["exact"],
            "group": ["exact"],
            "student": ["exact"],
            "course_enrollment": ["exact"],
        }
