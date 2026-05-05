from __future__ import annotations

from rest_framework import serializers

from apps.education.models import AcademicYear, EducationPeriod
from apps.organizations.models import Organization
from apps.schedule.constants import GenerationSource, ImportSourceType
from apps.schedule.models import ScheduleGenerationBatch, ScheduleImportBatch


class ScheduleImportBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleImportBatch
        fields = (
            "id",
            "organization",
            "academic_year",
            "education_period",
            "source_file",
            "source_type",
            "status",
            "imported_by",
            "started_at",
            "finished_at",
            "rows_total",
            "rows_success",
            "rows_failed",
            "log",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "imported_by",
            "started_at",
            "finished_at",
            "rows_total",
            "rows_success",
            "rows_failed",
            "log",
            "created_at",
            "updated_at",
        )


class ScheduleImportCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
    )
    education_period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        required=False,
        allow_null=True,
    )
    source_file = serializers.FileField(
        required=False,
        allow_empty_file=False,
    )
    source_type = serializers.ChoiceField(
        choices=ImportSourceType.choices,
        default=ImportSourceType.MANUAL,
    )


class ScheduleImportParseSerializer(ScheduleImportCreateSerializer):
    pass


class ScheduleImportApplySerializer(serializers.Serializer):
    dry_run = serializers.BooleanField(default=False)
    replace_existing = serializers.BooleanField(default=False)
    validate_conflicts = serializers.BooleanField(default=True)


class ScheduleGenerationBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleGenerationBatch
        fields = (
            "id",
            "organization",
            "academic_year",
            "education_period",
            "name",
            "source",
            "status",
            "generated_by",
            "started_at",
            "finished_at",
            "lessons_created",
            "lessons_updated",
            "conflicts_count",
            "dry_run",
            "log",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "generated_by",
            "started_at",
            "finished_at",
            "lessons_created",
            "lessons_updated",
            "conflicts_count",
            "log",
            "created_at",
            "updated_at",
        )


class ScheduleGenerationBatchCreateSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
    )
    education_period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        required=False,
        allow_null=True,
    )
    name = serializers.CharField(max_length=255)
    source = serializers.ChoiceField(
        choices=GenerationSource.choices,
        default=GenerationSource.PATTERNS,
    )
    dry_run = serializers.BooleanField(default=True)
