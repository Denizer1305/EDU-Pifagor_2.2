from __future__ import annotations

from rest_framework import serializers

from apps.education.models import AcademicYear, EducationPeriod


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = (
            "id",
            "name",
            "start_date",
            "end_date",
            "description",
            "is_current",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class EducationPeriodSerializer(serializers.ModelSerializer):
    academic_year = serializers.StringRelatedField(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        source="academic_year",
        write_only=True,
    )

    class Meta:
        model = EducationPeriod
        fields = (
            "id",
            "academic_year",
            "academic_year_id",
            "name",
            "code",
            "period_type",
            "sequence",
            "start_date",
            "end_date",
            "description",
            "is_current",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
