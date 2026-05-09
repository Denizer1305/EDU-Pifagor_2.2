from __future__ import annotations

from rest_framework import serializers

from apps.organizations.models import Department, Organization, OrganizationType


class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = (
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class OrganizationShortSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(source="type.name", read_only=True)

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "short_name",
            "type_name",
            "city",
            "is_active",
        )
        read_only_fields = fields


class OrganizationSerializer(serializers.ModelSerializer):
    type = OrganizationTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationType.objects.all(),
        source="type",
        write_only=True,
    )

    has_active_teacher_registration_code = serializers.BooleanField(read_only=True)

    class Meta:
        model = Organization
        fields = (
            "id",
            "type",
            "type_id",
            "name",
            "short_name",
            "description",
            "city",
            "address",
            "phone",
            "email",
            "website",
            "logo",
            "teacher_registration_code_is_active",
            "teacher_registration_code_expires_at",
            "has_active_teacher_registration_code",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "has_active_teacher_registration_code",
            "created_at",
            "updated_at",
        )


class OrganizationTeacherRegistrationCodeSerializer(serializers.Serializer):
    teacher_registration_code = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        max_length=128,
    )
    teacher_registration_code_expires_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    def validate_teacher_registration_code(self, value):
        return value.strip()


class DepartmentSerializer(serializers.ModelSerializer):
    organization = OrganizationShortSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="organization",
        write_only=True,
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "organization",
            "organization_id",
            "name",
            "short_name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        return value.strip()

    def validate_short_name(self, value):
        return value.strip()

    def validate_description(self, value):
        return value.strip()
