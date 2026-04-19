from __future__ import annotations

from rest_framework import serializers

from apps.education.models import AcademicYear, Curriculum, CurriculumItem, EducationPeriod
from apps.organizations.models import Department, Organization, Subject


class CurriculumSerializer(serializers.ModelSerializer):
    organization = serializers.StringRelatedField(read_only=True)
    department = serializers.StringRelatedField(read_only=True)
    academic_year = serializers.StringRelatedField(read_only=True)

    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="organization",
        write_only=True,
    )
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        write_only=True,
        allow_null=True,
        required=False,
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        source="academic_year",
        write_only=True,
    )

    class Meta:
        model = Curriculum
        fields = (
            "id", "organization",
            "organization_id", "department",
            "department_id", "academic_year",
            "academic_year_id", "code",
            "name", "description",
            "total_hours", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )


class CurriculumItemSerializer(serializers.ModelSerializer):
    curriculum = serializers.StringRelatedField(read_only=True)
    period = serializers.StringRelatedField(read_only=True)
    subject = serializers.StringRelatedField(read_only=True)

    curriculum_id = serializers.PrimaryKeyRelatedField(
        queryset=Curriculum.objects.all(),
        source="curriculum",
        write_only=True,
    )
    period_id = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        source="period",
        write_only=True,
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subject",
        write_only=True,
    )

    class Meta:
        model = CurriculumItem
        fields = (
            "id", "curriculum",
            "curriculum_id", "period",
            "period_id", "subject",
            "subject_id", "sequence",
            "planned_hours", "contact_hours",
            "independent_hours", "assessment_type",
            "is_required", "is_active",
            "notes", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )
