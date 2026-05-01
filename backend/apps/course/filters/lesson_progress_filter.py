from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.course.filters.common import clean_search_value
from apps.course.models import LessonProgress


class LessonProgressFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    enrollment_id = django_filters.NumberFilter(field_name="enrollment_id")
    course_id = django_filters.NumberFilter(field_name="enrollment__course_id")
    lesson_id = django_filters.NumberFilter(field_name="lesson_id")
    module_id = django_filters.NumberFilter(field_name="lesson__module_id")
    student_id = django_filters.NumberFilter(field_name="enrollment__student_id")

    status = django_filters.CharFilter(field_name="status")
    has_score = django_filters.BooleanFilter(method="filter_has_score")
    is_completed = django_filters.BooleanFilter(method="filter_is_completed")

    class Meta:
        model = LessonProgress
        fields = (
            "enrollment_id",
            "course_id",
            "lesson_id",
            "module_id",
            "student_id",
            "status",
            "has_score",
            "is_completed",
        )

    def filter_q(self, queryset, name, value):
        value = clean_search_value(value)
        if not value:
            return queryset

        return queryset.filter(
            Q(lesson__title__icontains=value)
            | Q(lesson__subtitle__icontains=value)
            | Q(lesson__module__title__icontains=value)
            | Q(enrollment__student__email__icontains=value)
            | Q(enrollment__student__profile__first_name__icontains=value)
            | Q(enrollment__student__profile__last_name__icontains=value)
        ).distinct()

    def filter_has_score(self, queryset, name, value):
        if value is True:
            return queryset.filter(score__isnull=False)

        if value is False:
            return queryset.filter(score__isnull=True)

        return queryset

    def filter_is_completed(self, queryset, name, value):
        if value is True:
            return queryset.filter(completed_at__isnull=False)

        if value is False:
            return queryset.filter(completed_at__isnull=True)

        return queryset
