from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.course.filters.common import clean_search_value
from apps.course.models import CourseEnrollment


class CourseEnrollmentFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    course_id = django_filters.NumberFilter(field_name="course_id")
    student_id = django_filters.NumberFilter(field_name="student_id")
    assignment_id = django_filters.NumberFilter(field_name="assignment_id")
    status = django_filters.CharFilter(field_name="status")

    progress_from = django_filters.NumberFilter(field_name="progress_percent", lookup_expr="gte")
    progress_to = django_filters.NumberFilter(field_name="progress_percent", lookup_expr="lte")

    enrolled_at_from = django_filters.DateTimeFilter(field_name="enrolled_at", lookup_expr="gte")
    enrolled_at_to = django_filters.DateTimeFilter(field_name="enrolled_at", lookup_expr="lte")
    started_at_from = django_filters.DateTimeFilter(field_name="started_at", lookup_expr="gte")
    started_at_to = django_filters.DateTimeFilter(field_name="started_at", lookup_expr="lte")
    completed_at_from = django_filters.DateTimeFilter(field_name="completed_at", lookup_expr="gte")
    completed_at_to = django_filters.DateTimeFilter(field_name="completed_at", lookup_expr="lte")

    class Meta:
        model = CourseEnrollment
        fields = (
            "course_id",
            "student_id",
            "assignment_id",
            "status",
            "progress_from",
            "progress_to",
            "enrolled_at_from",
            "enrolled_at_to",
            "started_at_from",
            "started_at_to",
            "completed_at_from",
            "completed_at_to",
        )

    def filter_q(self, queryset, name, value):
        value = clean_search_value(value)
        if not value:
            return queryset

        return queryset.filter(
            Q(course__title__icontains=value)
            | Q(course__code__icontains=value)
            | Q(student__email__icontains=value)
            | Q(student__profile__first_name__icontains=value)
            | Q(student__profile__last_name__icontains=value)
        ).distinct()
