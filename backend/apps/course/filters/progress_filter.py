from __future__ import annotations

import django_filters

from apps.course.models import CourseProgress


class CourseProgressFilter(django_filters.FilterSet):
    course_id = django_filters.NumberFilter(field_name="enrollment__course_id")
    student_id = django_filters.NumberFilter(field_name="enrollment__student_id")

    progress_from = django_filters.NumberFilter(field_name="progress_percent", lookup_expr="gte")
    progress_to = django_filters.NumberFilter(field_name="progress_percent", lookup_expr="lte")

    has_activity = django_filters.BooleanFilter(method="filter_has_activity")
    is_completed = django_filters.BooleanFilter(method="filter_is_completed")

    class Meta:
        model = CourseProgress
        fields = (
            "course_id",
            "student_id",
            "progress_from",
            "progress_to",
            "has_activity",
            "is_completed",
        )

    def filter_has_activity(self, queryset, name, value):
        if value is True:
            return queryset.filter(last_activity_at__isnull=False)

        if value is False:
            return queryset.filter(last_activity_at__isnull=True)

        return queryset

    def filter_is_completed(self, queryset, name, value):
        if value is True:
            return queryset.filter(completed_at__isnull=False)

        if value is False:
            return queryset.filter(completed_at__isnull=True)

        return queryset
