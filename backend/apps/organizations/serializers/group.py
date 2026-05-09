from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Department, Group, GroupCurator, Organization

User = get_user_model()


class GroupOrganizationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "short_name",
        )
        read_only_fields = fields


class GroupDepartmentShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "short_name",
        )
        read_only_fields = fields


class GroupSerializer(serializers.ModelSerializer):
    organization = GroupOrganizationShortSerializer(read_only=True)
    department = GroupDepartmentShortSerializer(read_only=True)

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

    has_active_join_code = serializers.BooleanField(read_only=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "organization",
            "organization_id",
            "department",
            "department_id",
            "name",
            "code",
            "study_form",
            "course_number",
            "admission_year",
            "graduation_year",
            "academic_year",
            "status",
            "description",
            "join_code_is_active",
            "join_code_expires_at",
            "has_active_join_code",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "has_active_join_code",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        return value.strip()

    def validate_code(self, value):
        return value.strip()

    def validate_academic_year(self, value):
        return value.strip()

    def validate_description(self, value):
        return value.strip()


class GroupJoinCodeSerializer(serializers.Serializer):
    join_code = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        max_length=128,
    )
    join_code_expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    def validate_join_code(self, value):
        return value.strip()


class GroupCuratorSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    teacher_full_name = serializers.CharField(
        source="teacher.full_name", read_only=True
    )
    is_current = serializers.BooleanField(read_only=True)

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
            "id",
            "group",
            "group_id",
            "teacher_id",
            "teacher_email",
            "teacher_full_name",
            "is_primary",
            "is_active",
            "starts_at",
            "ends_at",
            "notes",
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

    def validate_notes(self, value):
        return value.strip()
