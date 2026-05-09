from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import (
    Organization,
    Subject,
    TeacherOrganization,
    TeacherSubject,
)

User = get_user_model()


class TeacherOrganizationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "short_name",
        )
        read_only_fields = fields


class TeacherOrganizationSerializer(serializers.ModelSerializer):
    organization = TeacherOrganizationShortSerializer(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.CharField(
        source="teacher.full_name", read_only=True
    )
    is_current = serializers.BooleanField(read_only=True)

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
            "id",
            "teacher_id",
            "teacher_email",
            "teacher_full_name",
            "organization",
            "organization_id",
            "position",
            "employment_type",
            "is_primary",
            "starts_at",
            "ends_at",
            "notes",
            "is_active",
            "is_current",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "is_current",
            "created_at",
            "updated_at",
        )

    def validate_position(self, value):
        return value.strip()

    def validate_notes(self, value):
        return value.strip()


class TeacherSubjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = (
            "id",
            "name",
            "short_name",
        )
        read_only_fields = fields


class TeacherSubjectSerializer(serializers.ModelSerializer):
    subject = TeacherSubjectShortSerializer(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.CharField(
        source="teacher.full_name", read_only=True
    )

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
            "id",
            "teacher_id",
            "teacher_email",
            "teacher_full_name",
            "subject",
            "subject_id",
            "is_primary",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
