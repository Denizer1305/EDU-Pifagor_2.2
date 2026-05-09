from __future__ import annotations

from rest_framework import serializers

from apps.education.models import AcademicYear, EducationPeriod
from apps.organizations.models import Organization
from apps.schedule.models import SchedulePattern
from apps.schedule.serializers.audience import SchedulePatternAudienceSerializer
from apps.schedule.serializers.room import ScheduleRoomShortSerializer
from apps.schedule.serializers.time_slot import ScheduleTimeSlotShortSerializer


class SchedulePatternShortSerializer(serializers.ModelSerializer):
    time_slot = ScheduleTimeSlotShortSerializer(read_only=True)
    room = ScheduleRoomShortSerializer(read_only=True)
    group_name = serializers.CharField(source="group", read_only=True)
    subject_name = serializers.CharField(source="subject", read_only=True)
    teacher_name = serializers.CharField(source="teacher", read_only=True)

    class Meta:
        model = SchedulePattern
        fields = (
            "id",
            "weekday",
            "time_slot",
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
            "is_active",
        )


class SchedulePatternSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year", read_only=True)
    education_period_name = serializers.CharField(
        source="education_period", read_only=True
    )
    week_template_name = serializers.CharField(source="week_template", read_only=True)
    group_name = serializers.CharField(source="group", read_only=True)
    subject_name = serializers.CharField(source="subject", read_only=True)
    teacher_name = serializers.CharField(source="teacher", read_only=True)
    room_detail = ScheduleRoomShortSerializer(source="room", read_only=True)
    time_slot_detail = ScheduleTimeSlotShortSerializer(
        source="time_slot", read_only=True
    )
    course_name = serializers.CharField(source="course", read_only=True)
    course_lesson_name = serializers.CharField(source="course_lesson", read_only=True)
    audiences = SchedulePatternAudienceSerializer(many=True, read_only=True)

    class Meta:
        model = SchedulePattern
        fields = (
            "id",
            "organization",
            "organization_name",
            "academic_year",
            "academic_year_name",
            "education_period",
            "education_period_name",
            "week_template",
            "week_template_name",
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
            "title",
            "lesson_type",
            "source_type",
            "status",
            "starts_on",
            "ends_on",
            "repeat_rule",
            "priority",
            "is_active",
            "notes",
            "audiences",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class SchedulePatternCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulePattern
        fields = (
            "organization",
            "academic_year",
            "education_period",
            "week_template",
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
            "title",
            "lesson_type",
            "source_type",
            "status",
            "starts_on",
            "ends_on",
            "repeat_rule",
            "priority",
            "is_active",
            "notes",
        )

    def validate(self, attrs: dict) -> dict:
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        starts_on = attrs.get("starts_on", getattr(self.instance, "starts_on", None))
        ends_on = attrs.get("ends_on", getattr(self.instance, "ends_on", None))

        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError(
                {"ends_at": "Время окончания должно быть позже времени начала."}
            )

        if starts_on and ends_on and ends_on < starts_on:
            raise serializers.ValidationError(
                {"ends_on": "Дата окончания не может быть раньше даты начала."}
            )

        return attrs


class SchedulePatternCopySerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
    )
    source_education_period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
    )
    target_education_period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
    )

    def validate(self, attrs):
        if attrs["source_education_period"] == attrs["target_education_period"]:
            raise serializers.ValidationError(
                {
                    "target_education_period": (
                        "Период назначения должен отличаться от исходного периода."
                    )
                }
            )

        return attrs
