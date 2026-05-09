from __future__ import annotations

from rest_framework import serializers

from apps.schedule.models import ScheduleRoom


class ScheduleRoomShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleRoom
        fields = (
            "id",
            "name",
            "number",
            "room_type",
            "capacity",
            "building",
            "floor",
        )


class ScheduleRoomSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)
    department_name = serializers.CharField(source="department", read_only=True)

    class Meta:
        model = ScheduleRoom
        fields = (
            "id",
            "organization",
            "organization_name",
            "department",
            "department_name",
            "name",
            "number",
            "room_type",
            "capacity",
            "floor",
            "building",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ScheduleRoomCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleRoom
        fields = (
            "organization",
            "department",
            "name",
            "number",
            "room_type",
            "capacity",
            "floor",
            "building",
            "is_active",
            "notes",
        )

    def validate_capacity(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError(
                "Вместимость не может быть отрицательной."
            )
        return value
