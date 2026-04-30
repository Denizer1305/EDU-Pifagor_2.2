from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.course.models import (
    Course,
    CourseAssignment,
    CourseEnrollment,
    CourseProgress,
    LessonProgress,
)


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
        value = (value or "").strip()
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


class CourseAssignmentFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    course_id = django_filters.NumberFilter(field_name="course_id")
    group_id = django_filters.NumberFilter(field_name="group_id")
    student_id = django_filters.NumberFilter(field_name="student_id")
    assigned_by_id = django_filters.NumberFilter(field_name="assigned_by_id")

    assignment_type = django_filters.CharFilter(field_name="assignment_type")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    auto_enroll = django_filters.BooleanFilter(field_name="auto_enroll")

    starts_at_from = django_filters.DateTimeFilter(field_name="starts_at", lookup_expr="gte")
    starts_at_to = django_filters.DateTimeFilter(field_name="starts_at", lookup_expr="lte")
    ends_at_from = django_filters.DateTimeFilter(field_name="ends_at", lookup_expr="gte")
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
        value = (value or "").strip()
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
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(course__title__icontains=value)
            | Q(course__code__icontains=value)
            | Q(student__email__icontains=value)
            | Q(student__profile__first_name__icontains=value)
            | Q(student__profile__last_name__icontains=value)
        ).distinct()


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
        value = (value or "").strip()
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
