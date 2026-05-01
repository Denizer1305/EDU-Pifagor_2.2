from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.course.filters.common import clean_search_value
from apps.course.models import Course


class CourseFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    status = django_filters.CharFilter(field_name="status")
    visibility = django_filters.CharFilter(field_name="visibility")
    course_type = django_filters.CharFilter(field_name="course_type")
    origin = django_filters.CharFilter(field_name="origin")
    level = django_filters.CharFilter(field_name="level")
    language = django_filters.CharFilter(field_name="language")

    author_id = django_filters.NumberFilter(field_name="author_id")
    teacher_id = django_filters.NumberFilter(method="filter_teacher_id")
    organization_id = django_filters.NumberFilter(field_name="organization_id")
    subject_id = django_filters.NumberFilter(field_name="subject_id")
    academic_year_id = django_filters.NumberFilter(field_name="academic_year_id")
    period_id = django_filters.NumberFilter(field_name="period_id")
    group_subject_id = django_filters.NumberFilter(field_name="group_subject_id")

    is_template = django_filters.BooleanFilter(field_name="is_template")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    allow_self_enrollment = django_filters.BooleanFilter(field_name="allow_self_enrollment")
    has_cover = django_filters.BooleanFilter(method="filter_has_cover")

    created_at_from = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    published_at_from = django_filters.DateTimeFilter(field_name="published_at", lookup_expr="gte")
    published_at_to = django_filters.DateTimeFilter(field_name="published_at", lookup_expr="lte")

    class Meta:
        model = Course
        fields = (
            "status",
            "visibility",
            "course_type",
            "origin",
            "level",
            "language",
            "author_id",
            "teacher_id",
            "organization_id",
            "subject_id",
            "academic_year_id",
            "period_id",
            "group_subject_id",
            "is_template",
            "is_active",
            "allow_self_enrollment",
            "has_cover",
            "created_at_from",
            "created_at_to",
            "published_at_from",
            "published_at_to",
        )

    def filter_q(self, queryset, name, value):
        value = clean_search_value(value)
        if not value:
            return queryset

        return queryset.filter(
            Q(title__icontains=value)
            | Q(subtitle__icontains=value)
            | Q(description__icontains=value)
            | Q(code__icontains=value)
            | Q(slug__icontains=value)
            | Q(author__email__icontains=value)
            | Q(author__profile__first_name__icontains=value)
            | Q(author__profile__last_name__icontains=value)
            | Q(organization__name__icontains=value)
            | Q(organization__short_name__icontains=value)
            | Q(subject__name__icontains=value)
            | Q(subject__short_name__icontains=value)
        ).distinct()

    def filter_teacher_id(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(
            course_teachers__teacher_id=value,
            course_teachers__is_active=True,
        ).distinct()

    def filter_has_cover(self, queryset, name, value):
        if value is True:
            return queryset.exclude(cover_image="")

        if value is False:
            return queryset.filter(Q(cover_image="") | Q(cover_image__isnull=True))

        return queryset
