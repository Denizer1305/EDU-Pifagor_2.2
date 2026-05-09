from __future__ import annotations

from rest_framework import serializers

from apps.organizations.models import Organization
from apps.schedule.constants import EducationLevel
from apps.schedule.models import ScheduleTimeSlot


class ScheduleTimeSlotShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleTimeSlot
        fields = (
            "id",
            "name",
            "number",
            "starts_at",
            "ends_at",
            "duration_minutes",
            "education_level",
            "is_pair",
        )


class ScheduleTimeSlotSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)

    class Meta:
        model = ScheduleTimeSlot
        fields = (
            "id",
            "organization",
            "organization_name",
            "name",
            "number",
            "starts_at",
            "ends_at",
            "duration_minutes",
            "education_level",
            "is_pair",
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

    def validate(self, attrs: dict) -> dict:
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))

        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError(
                {"ends_at": "Время окончания должно быть позже времени начала."}
            )

        return attrs


class ScheduleTimeSlotCreateUpdateSerializer(ScheduleTimeSlotSerializer):
    class Meta(ScheduleTimeSlotSerializer.Meta):
        fields = (
            "organization",
            "name",
            "number",
            "starts_at",
            "ends_at",
            "duration_minutes",
            "education_level",
            "is_pair",
            "is_active",
            "notes",
        )
        read_only_fields = ()


class ScheduleTimeSlotBulkCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
    )
    education_level = serializers.ChoiceField(
        choices=EducationLevel.choices,
        required=False,
        default=EducationLevel.MIXED,
    )
    is_pair = serializers.BooleanField(required=False, default=False)
    overwrite = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs: dict) -> dict:
        attrs.setdefault(
            "education_level",
            ScheduleTimeSlot._meta.get_field("education_level").default,
        )
        attrs.setdefault("is_pair", False)
        return attrs
