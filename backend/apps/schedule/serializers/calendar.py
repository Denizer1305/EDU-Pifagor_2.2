from __future__ import annotations

from rest_framework import serializers

from apps.schedule.models import ScheduleCalendar, ScheduleWeekTemplate


def validate_date_range(attrs: dict, *, instance=None) -> dict:
    starts_on = attrs.get("starts_on", getattr(instance, "starts_on", None))
    ends_on = attrs.get("ends_on", getattr(instance, "ends_on", None))

    if starts_on and ends_on and ends_on < starts_on:
        raise serializers.ValidationError(
            {"ends_on": "Дата окончания не может быть раньше даты начала."}
        )

    return attrs


class ScheduleCalendarShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleCalendar
        fields = (
            "id",
            "name",
            "calendar_type",
            "starts_on",
            "ends_on",
            "is_active",
        )


class ScheduleCalendarSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year", read_only=True)
    education_period_name = serializers.CharField(
        source="education_period",
        read_only=True,
    )

    class Meta:
        model = ScheduleCalendar
        fields = (
            "id",
            "organization",
            "organization_name",
            "academic_year",
            "academic_year_name",
            "education_period",
            "education_period_name",
            "name",
            "calendar_type",
            "starts_on",
            "ends_on",
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
        return validate_date_range(attrs, instance=self.instance)


class ScheduleCalendarCreateUpdateSerializer(ScheduleCalendarSerializer):
    class Meta(ScheduleCalendarSerializer.Meta):
        fields = (
            "organization",
            "academic_year",
            "education_period",
            "name",
            "calendar_type",
            "starts_on",
            "ends_on",
            "is_active",
            "notes",
        )
        read_only_fields = ()


class ScheduleCalendarMarkSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=ScheduleCalendar._meta.get_field(
            "organization"
        ).remote_field.model.objects.all()
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=ScheduleCalendar._meta.get_field(
            "academic_year"
        ).remote_field.model.objects.all()
    )
    education_period = serializers.PrimaryKeyRelatedField(
        queryset=ScheduleCalendar._meta.get_field(
            "education_period"
        ).remote_field.model.objects.all(),
        required=False,
        allow_null=True,
    )
    starts_on = serializers.DateField()
    ends_on = serializers.DateField(required=False)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs: dict) -> dict:
        if attrs.get("ends_on") is None:
            attrs["ends_on"] = attrs["starts_on"]

        return validate_date_range(attrs)


class ScheduleWeekTemplateShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleWeekTemplate
        fields = (
            "id",
            "name",
            "week_type",
            "is_default",
            "is_active",
        )


class ScheduleWeekTemplateSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year", read_only=True)
    education_period_name = serializers.CharField(
        source="education_period",
        read_only=True,
    )

    class Meta:
        model = ScheduleWeekTemplate
        fields = (
            "id",
            "organization",
            "organization_name",
            "academic_year",
            "academic_year_name",
            "education_period",
            "education_period_name",
            "name",
            "week_type",
            "starts_on",
            "ends_on",
            "is_default",
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
        return validate_date_range(attrs, instance=self.instance)


class ScheduleWeekTemplateCreateUpdateSerializer(ScheduleWeekTemplateSerializer):
    class Meta(ScheduleWeekTemplateSerializer.Meta):
        fields = (
            "organization",
            "academic_year",
            "education_period",
            "name",
            "week_type",
            "starts_on",
            "ends_on",
            "is_default",
            "is_active",
            "notes",
        )
        read_only_fields = ()
