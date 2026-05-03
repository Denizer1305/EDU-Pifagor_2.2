from __future__ import annotations

from rest_framework import serializers

from apps.journal.models import JournalSummary


class JournalSummaryListSerializer(serializers.ModelSerializer):
    """Краткое представление сводки журнала."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = JournalSummary
        fields = (
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "student",
            "student_email",
            "attendance_percent",
            "avg_score",
            "debt_count",
            "progress_percent",
            "calculated_at",
        )


class JournalSummaryDetailSerializer(serializers.ModelSerializer):
    """Детальное представление сводки журнала."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = JournalSummary
        fields = (
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "student",
            "student_email",
            "total_lessons",
            "attended_lessons",
            "absent_lessons",
            "attendance_percent",
            "avg_score",
            "debt_count",
            "total_topics",
            "completed_topics",
            "topics_behind",
            "progress_percent",
            "calculated_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
