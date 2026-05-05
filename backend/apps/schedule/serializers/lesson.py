from __future__ import annotations

from rest_framework import serializers

from apps.schedule.models import ScheduledLesson
from apps.schedule.serializers.audience import ScheduledLessonAudienceSerializer
from apps.schedule.serializers.room import ScheduleRoomShortSerializer
from apps.schedule.serializers.time_slot import ScheduleTimeSlotShortSerializer


class ScheduledLessonShortSerializer(serializers.ModelSerializer):
    time_slot = ScheduleTimeSlotShortSerializer(read_only=True)
    room = ScheduleRoomShortSerializer(read_only=True)
    group_name = serializers.CharField(source="group", read_only=True)
    subject_name = serializers.CharField(source="subject", read_only=True)
    teacher_name = serializers.CharField(source="teacher", read_only=True)

    class Meta:
        model = ScheduledLesson
        fields = (
            "id",
            "date",
            "weekday",
            "time_slot",
            "starts_at",
            "ends_at",
            "group",
            "group_name",
            "subject",
            "subject_name",
            "teacher",
            "teacher_name",
            "room",
            "title",
            "lesson_type",
            "status",
            "is_public",
            "is_locked",
        )


class ScheduledLessonSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year", read_only=True)
    education_period_name = serializers.CharField(
        source="education_period", read_only=True
    )
    group_name = serializers.CharField(source="group", read_only=True)
    subject_name = serializers.CharField(source="subject", read_only=True)
    teacher_name = serializers.CharField(source="teacher", read_only=True)
    room_detail = ScheduleRoomShortSerializer(source="room", read_only=True)
    time_slot_detail = ScheduleTimeSlotShortSerializer(
        source="time_slot", read_only=True
    )
    course_name = serializers.CharField(source="course", read_only=True)
    course_lesson_name = serializers.CharField(source="course_lesson", read_only=True)
    journal_lesson_name = serializers.CharField(source="journal_lesson", read_only=True)
    audiences = ScheduledLessonAudienceSerializer(many=True, read_only=True)

    class Meta:
        model = ScheduledLesson
        fields = (
            "id",
            "organization",
            "organization_name",
            "academic_year",
            "academic_year_name",
            "education_period",
            "education_period_name",
            "pattern",
            "date",
            "weekday",
            "time_slot",
            "time_slot_detail",
            "starts_at",
            "ends_at",
            "group",
            "group_name",
            "subject",
            "subject_name",
            "teacher",
            "teacher_name",
            "room",
            "room_detail",
            "group_subject",
            "teacher_group_subject",
            "course",
            "course_name",
            "course_lesson",
            "course_lesson_name",
            "journal_lesson",
            "journal_lesson_name",
            "title",
            "planned_topic",
            "lesson_type",
            "source_type",
            "status",
            "generated_from_pattern",
            "generation_batch",
            "is_locked",
            "is_public",
            "created_by",
            "updated_by",
            "notes",
            "audiences",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "generated_from_pattern",
            "generation_batch",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )


class ScheduledLessonCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledLesson
        fields = (
            "organization",
            "academic_year",
            "education_period",
            "pattern",
            "date",
            "weekday",
            "time_slot",
            "starts_at",
            "ends_at",
            "group",
            "subject",
            "teacher",
            "room",
            "group_subject",
            "teacher_group_subject",
            "course",
            "course_lesson",
            "journal_lesson",
            "title",
            "planned_topic",
            "lesson_type",
            "source_type",
            "status",
            "is_locked",
            "is_public",
            "notes",
        )

    def validate(self, attrs: dict) -> dict:
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))

        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError(
                {"ends_at": "Время окончания должно быть позже времени начала."}
            )

        return attrs


class ScheduledLessonStatusSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    comment = serializers.CharField(required=False, allow_blank=True)


class ScheduledLessonRescheduleSerializer(serializers.Serializer):
    date = serializers.DateField()
    time_slot = serializers.IntegerField(required=False)
    starts_at = serializers.TimeField(required=False)
    ends_at = serializers.TimeField(required=False)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    comment = serializers.CharField(required=False, allow_blank=True)


class ScheduledLessonReplaceTeacherSerializer(serializers.Serializer):
    teacher = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    comment = serializers.CharField(required=False, allow_blank=True)


class ScheduledLessonChangeRoomSerializer(serializers.Serializer):
    room = serializers.IntegerField()
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    comment = serializers.CharField(required=False, allow_blank=True)
