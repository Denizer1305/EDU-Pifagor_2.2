from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.journal.models import (
    AttendanceRecord,
    JournalGrade,
    JournalLesson,
    JournalSummary,
    TopicProgress,
)
from apps.journal.models.choices import (
    AttendanceStatus,
    GradeScale,
    GradeType,
    JournalLessonStatus,
    TopicProgressStatus,
)


class JournalLessonFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="course_id")
    group = django_filters.NumberFilter(field_name="group_id")
    teacher = django_filters.NumberFilter(field_name="teacher_id")
    status = django_filters.ChoiceFilter(choices=JournalLessonStatus.choices)

    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = JournalLesson
        fields = (
            "course",
            "group",
            "teacher",
            "status",
            "date_from",
            "date_to",
            "search",
        )

    def filter_search(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(planned_topic__icontains=value)
            | Q(actual_topic__icontains=value)
            | Q(homework__icontains=value)
            | Q(teacher_comment__icontains=value)
            | Q(course__title__icontains=value)
            | Q(course__code__icontains=value)
            | Q(group__name__icontains=value)
            | Q(group__code__icontains=value)
            | Q(teacher__email__icontains=value)
        )


class AttendanceRecordFilter(django_filters.FilterSet):
    lesson = django_filters.NumberFilter(field_name="lesson_id")
    student = django_filters.NumberFilter(field_name="student_id")
    course = django_filters.NumberFilter(field_name="lesson__course_id")
    group = django_filters.NumberFilter(field_name="lesson__group_id")
    status = django_filters.ChoiceFilter(choices=AttendanceStatus.choices)

    date_from = django_filters.DateFilter(field_name="lesson__date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="lesson__date", lookup_expr="lte")

    class Meta:
        model = AttendanceRecord
        fields = (
            "lesson",
            "student",
            "course",
            "group",
            "status",
            "date_from",
            "date_to",
        )


class JournalGradeFilter(django_filters.FilterSet):
    lesson = django_filters.NumberFilter(field_name="lesson_id")
    student = django_filters.NumberFilter(field_name="student_id")
    course = django_filters.NumberFilter(field_name="lesson__course_id")
    group = django_filters.NumberFilter(field_name="lesson__group_id")
    teacher = django_filters.NumberFilter(field_name="lesson__teacher_id")

    grade_type = django_filters.ChoiceFilter(choices=GradeType.choices)
    scale = django_filters.ChoiceFilter(choices=GradeScale.choices)
    is_auto = django_filters.BooleanFilter()

    date_from = django_filters.DateFilter(field_name="lesson__date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="lesson__date", lookup_expr="lte")

    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = JournalGrade
        fields = (
            "lesson",
            "student",
            "course",
            "group",
            "teacher",
            "grade_type",
            "scale",
            "is_auto",
            "date_from",
            "date_to",
            "search",
        )

    def filter_search(self, queryset, name, value):
        value = value.strip()

        if not value:
            return queryset

        return queryset.filter(
            Q(comment__icontains=value)
            | Q(lesson__planned_topic__icontains=value)
            | Q(lesson__actual_topic__icontains=value)
            | Q(lesson__course__title__icontains=value)
            | Q(lesson__course__code__icontains=value)
            | Q(lesson__group__name__icontains=value)
            | Q(lesson__group__code__icontains=value)
            | Q(student__email__icontains=value)
            | Q(graded_by__email__icontains=value)
        )


class TopicProgressFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="course_id")
    group = django_filters.NumberFilter(field_name="group_id")
    lesson = django_filters.NumberFilter(field_name="lesson_id")
    journal_lesson = django_filters.NumberFilter(field_name="journal_lesson_id")

    status = django_filters.ChoiceFilter(choices=TopicProgressStatus.choices)
    only_behind = django_filters.BooleanFilter(method="filter_only_behind")

    planned_date_from = django_filters.DateFilter(
        field_name="planned_date",
        lookup_expr="gte",
    )
    planned_date_to = django_filters.DateFilter(
        field_name="planned_date",
        lookup_expr="lte",
    )

    actual_date_from = django_filters.DateFilter(
        field_name="actual_date",
        lookup_expr="gte",
    )
    actual_date_to = django_filters.DateFilter(
        field_name="actual_date",
        lookup_expr="lte",
    )

    class Meta:
        model = TopicProgress
        fields = (
            "course",
            "group",
            "lesson",
            "journal_lesson",
            "status",
            "only_behind",
            "planned_date_from",
            "planned_date_to",
            "actual_date_from",
            "actual_date_to",
        )

    def filter_only_behind(self, queryset, name, value):
        if value:
            return queryset.filter(days_behind__gt=0)

        return queryset


class JournalSummaryFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="course_id")
    group = django_filters.NumberFilter(field_name="group_id")
    student = django_filters.NumberFilter(field_name="student_id")

    only_group_summary = django_filters.BooleanFilter(
        method="filter_only_group_summary",
    )
    only_student_summary = django_filters.BooleanFilter(
        method="filter_only_student_summary",
    )

    class Meta:
        model = JournalSummary
        fields = (
            "course",
            "group",
            "student",
            "only_group_summary",
            "only_student_summary",
        )

    def filter_only_group_summary(self, queryset, name, value):
        if value:
            return queryset.filter(student__isnull=True)

        return queryset

    def filter_only_student_summary(self, queryset, name, value):
        if value:
            return queryset.filter(student__isnull=False)

        return queryset
