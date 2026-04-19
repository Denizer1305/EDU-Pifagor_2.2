from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Organization, Subject, TeacherOrganization, TeacherSubject

User = get_user_model()


class TeacherOrganizationSerializer(serializers.ModelSerializer):
    organization = serializers.StringRelatedField(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.CharField(source="teacher.full_name", read_only=True)

    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="organization",
        write_only=True,
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="teacher",
        write_only=True,
    )

    class Meta:
        model = TeacherOrganization
        fields = (
            "id", "teacher_id",
            "teacher_email", "teacher_full_name",
            "organization", "organization_id",
            "employment_type", "is_primary",
            "starts_at", "ends_at",
            "notes", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )


class TeacherSubjectSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.CharField(source="teacher.full_name", read_only=True)

    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subject",
        write_only=True,
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="teacher",
        write_only=True,
    )

    class Meta:
        model = TeacherSubject
        fields = (
            "id", "teacher_id",
            "teacher_email", "teacher_full_name",
            "subject", "subject_id",
            "is_primary", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )
