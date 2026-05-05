from __future__ import annotations

from rest_framework import serializers

from apps.schedule.models import ScheduleChange
from apps.schedule.serializers.room import ScheduleRoomShortSerializer
from apps.schedule.serializers.time_slot import ScheduleTimeSlotShortSerializer


class ScheduleChangeSerializer(serializers.ModelSerializer):
    old_time_slot_detail = ScheduleTimeSlotShortSerializer(
        source="old_time_slot", read_only=True
    )
    new_time_slot_detail = ScheduleTimeSlotShortSerializer(
        source="new_time_slot", read_only=True
    )
    old_room_detail = ScheduleRoomShortSerializer(source="old_room", read_only=True)
    new_room_detail = ScheduleRoomShortSerializer(source="new_room", read_only=True)
    old_teacher_name = serializers.CharField(source="old_teacher", read_only=True)
    new_teacher_name = serializers.CharField(source="new_teacher", read_only=True)
    changed_by_name = serializers.CharField(source="changed_by", read_only=True)

    class Meta:
        model = ScheduleChange
        fields = (
            "id",
            "scheduled_lesson",
            "change_type",
            "old_date",
            "new_date",
            "old_time_slot",
            "old_time_slot_detail",
            "new_time_slot",
            "new_time_slot_detail",
            "old_starts_at",
            "new_starts_at",
            "old_ends_at",
            "new_ends_at",
            "old_room",
            "old_room_detail",
            "new_room",
            "new_room_detail",
            "old_teacher",
            "old_teacher_name",
            "new_teacher",
            "new_teacher_name",
            "reason",
            "changed_by",
            "changed_by_name",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ScheduleChangeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleChange
        fields = (
            "scheduled_lesson",
            "change_type",
            "old_date",
            "new_date",
            "old_time_slot",
            "new_time_slot",
            "old_starts_at",
            "new_starts_at",
            "old_ends_at",
            "new_ends_at",
            "old_room",
            "new_room",
            "old_teacher",
            "new_teacher",
            "reason",
            "changed_by",
            "comment",
        )
