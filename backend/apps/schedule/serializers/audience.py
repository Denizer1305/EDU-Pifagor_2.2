from __future__ import annotations

from rest_framework import serializers

from apps.schedule.models import ScheduledLessonAudience, SchedulePatternAudience


class SchedulePatternAudienceSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group", read_only=True)
    student_name = serializers.CharField(source="student", read_only=True)
    course_enrollment_name = serializers.CharField(
        source="course_enrollment", read_only=True
    )

    class Meta:
        model = SchedulePatternAudience
        fields = (
            "id",
            "pattern",
            "audience_type",
            "group",
            "group_name",
            "subgroup_name",
            "student",
            "student_name",
            "course_enrollment",
            "course_enrollment_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class SchedulePatternAudienceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulePatternAudience
        fields = (
            "pattern",
            "audience_type",
            "group",
            "subgroup_name",
            "student",
            "course_enrollment",
            "notes",
        )


class ScheduledLessonAudienceSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group", read_only=True)
    student_name = serializers.CharField(source="student", read_only=True)
    course_enrollment_name = serializers.CharField(
        source="course_enrollment", read_only=True
    )

    class Meta:
        model = ScheduledLessonAudience
        fields = (
            "id",
            "scheduled_lesson",
            "audience_type",
            "group",
            "group_name",
            "subgroup_name",
            "student",
            "student_name",
            "course_enrollment",
            "course_enrollment_name",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ScheduledLessonAudienceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledLessonAudience
        fields = (
            "scheduled_lesson",
            "audience_type",
            "group",
            "subgroup_name",
            "student",
            "course_enrollment",
            "notes",
        )
