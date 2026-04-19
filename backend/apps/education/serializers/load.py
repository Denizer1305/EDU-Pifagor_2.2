from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.education.models import AcademicYear, EducationPeriod, GroupSubject, TeacherGroupSubject
from apps.organizations.models import Group, Subject

User = get_user_model()


class GroupSubjectSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)
    subject = serializers.StringRelatedField(read_only=True)
    academic_year = serializers.StringRelatedField(read_only=True)
    period = serializers.StringRelatedField(read_only=True)

    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="group",
        write_only=True,
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subject",
        write_only=True,
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        source="academic_year",
        write_only=True,
    )
    period_id = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        source="period",
        write_only=True,
    )

    class Meta:
        model = GroupSubject
        fields = (
            "id", "group",
            "group_id", "subject",
            "subject_id", "academic_year",
            "academic_year_id", "period",
            "period_id", "planned_hours",
            "contact_hours", "independent_hours",
            "assessment_type", "is_required",
            "is_active", "notes",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )


class TeacherGroupSubjectSerializer(serializers.ModelSerializer):
    teacher_email = serializers.EmailField(
        source="teacher.email",
        read_only=True,
    )
    teacher_full_name = serializers.CharField(
        source="teacher.full_name",
        read_only=True,
    )
    group_subject = serializers.StringRelatedField(read_only=True)

    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="teacher",
        write_only=True,
    )
    group_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=GroupSubject.objects.all(),
        source="group_subject",
        write_only=True,
    )

    class Meta:
        model = TeacherGroupSubject
        fields = (
            "id", "teacher_id",
            "teacher_email", "teacher_full_name",
            "group_subject", "group_subject_id",
            "role", "is_primary",
            "is_active", "planned_hours",
            "starts_at", "ends_at",
            "notes", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )
