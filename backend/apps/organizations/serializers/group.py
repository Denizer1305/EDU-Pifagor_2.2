from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Department, Group, GroupCurator, Organization

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    organization = serializers.StringRelatedField(read_only=True)
    department = serializers.StringRelatedField(read_only=True)

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

    class Meta:
        model = Group
        fields = (
            "id", "organization",
            "organization_id", "department",
            "department_id", "name",
            "code", "study_form",
            "course_number", "admission_year",
            "graduation_year", "academic_year",
            "status", "description",
            "is_active", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )


class GroupCuratorSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.CharField(source="teacher.full_name", read_only=True)

    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="group",
        write_only=True,
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="teacher",
        write_only=True,
    )

    class Meta:
        model = GroupCurator
        fields = (
            "id", "group",
            "group_id", "teacher_id",
            "teacher_email", "teacher_full_name",
            "is_primary", "starts_at",
            "ends_at", "notes",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )
