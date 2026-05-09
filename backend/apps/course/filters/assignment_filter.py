from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.course.filters.common import clean_search_value
from apps.course.models import CourseAssignment


class CourseAssignmentFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    course_id = django_filters.NumberFilter(field_name="course_id")
    group_id = django_filters.NumberFilter(field_name="group_id")
    student_id = django_filters.NumberFilter(field_name="student_id")
    assigned_by_id = django_filters.NumberFilter(field_name="assigned_by_id")

    assignment_type = django_filters.CharFilter(field_name="assignment_type")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    auto_enroll = django_filters.BooleanFilter(field_name="auto_enroll")

    starts_at_from = django_filters.DateTimeFilter(
        field_name="starts_at", lookup_expr="gte"
    )
    starts_at_to = django_filters.DateTimeFilter(
        field_name="starts_at", lookup_expr="lte"
    )
    ends_at_from = django_filters.DateTimeFilter(
        field_name="ends_at", lookup_expr="gte"
    )
    ends_at_to = django_filters.DateTimeFilter(field_name="ends_at", lookup_expr="lte")

    class Meta:
        model = CourseAssignment
        fields = (
            "course_id",
            "group_id",
            "student_id",
            "assigned_by_id",
            "assignment_type",
            "is_active",
            "auto_enroll",
            "starts_at_from",
            "starts_at_to",
            "ends_at_from",
            "ends_at_to",
        )

    def filter_q(self, queryset, name, value):
        value = clean_search_value(value)
        if not value:
            return queryset

        return queryset.filter(
            Q(course__title__icontains=value)
            | Q(course__code__icontains=value)
            | Q(group__name__icontains=value)
            | Q(group__code__icontains=value)
            | Q(student__email__icontains=value)
            | Q(student__profile__first_name__icontains=value)
            | Q(student__profile__last_name__icontains=value)
            | Q(assigned_by__email__icontains=value)
            | Q(notes__icontains=value)
        ).distinct()
