from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.education.models import AcademicYear, StudentGroupEnrollment
from apps.organizations.models import Group

User = get_user_model()


class StudentGroupEnrollmentSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(
        source="student.email",
        read_only=True,
    )
    student_full_name = serializers.CharField(
        source="student.full_name",
        read_only=True,
    )
    group = serializers.StringRelatedField(read_only=True)
    academic_year = serializers.StringRelatedField(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="student",
        write_only=True,
    )
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="group",
        write_only=True,
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        source="academic_year",
        write_only=True,
    )

    class Meta:
        model = StudentGroupEnrollment
        fields = (
            "id", "student_id",
            "student_email", "student_full_name",
            "group", "group_id",
            "academic_year", "academic_year_id",
            "enrollment_date", "completion_date",
            "status", "is_primary",
            "journal_number", "notes",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )
