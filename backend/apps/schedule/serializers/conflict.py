from __future__ import annotations

from rest_framework import serializers

from apps.schedule.models import ScheduleConflict
from apps.schedule.serializers.room import ScheduleRoomShortSerializer


class ScheduleConflictShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleConflict
        fields = (
            "id",
            "conflict_type",
            "severity",
            "status",
            "date",
            "starts_at",
            "ends_at",
            "message",
        )


class ScheduleConflictSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)
    teacher_name = serializers.CharField(source="teacher", read_only=True)
    group_name = serializers.CharField(source="group", read_only=True)
    room_detail = ScheduleRoomShortSerializer(source="room", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by", read_only=True)

    class Meta:
        model = ScheduleConflict
        fields = (
            "id",
            "organization",
            "organization_name",
            "conflict_type",
            "severity",
            "status",
            "lesson",
            "pattern",
            "related_lesson",
            "related_pattern",
            "teacher",
            "teacher_name",
            "room",
            "room_detail",
            "group",
            "group_name",
            "date",
            "starts_at",
            "ends_at",
            "message",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )


class ScheduleConflictCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleConflict
        fields = (
            "organization",
            "conflict_type",
            "severity",
            "status",
            "lesson",
            "pattern",
            "related_lesson",
            "related_pattern",
            "teacher",
            "room",
            "group",
            "date",
            "starts_at",
            "ends_at",
            "message",
            "notes",
        )


class ScheduleConflictResolveSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class ScheduleConflictIgnoreSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class ScheduleConflictDetectPeriodSerializer(serializers.Serializer):
    starts_on = serializers.DateField()
    ends_on = serializers.DateField()

    def validate(self, attrs):
        if attrs["ends_on"] < attrs["starts_on"]:
            raise serializers.ValidationError(
                {"ends_on": "Дата окончания не может быть раньше даты начала."}
            )

        return attrs
