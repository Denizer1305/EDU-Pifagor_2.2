from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.organizations.models import Department, Organization
from apps.users.models import TeacherProfile


class TeacherProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.profile.full_name", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = (
            "id", "user",
            "email", "full_name",
            "public_title", "short_bio",
            "bio", "education",
            "experience", "achievements",
            "is_public", "show_on_teachers_page",
            "requested_organization", "requested_department",
            "verification_status", "code_verified_at",
            "verified_by", "verified_at",
            "verification_comment", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "user",
            "email", "full_name",
            "verification_status", "code_verified_at",
            "verified_by", "verified_at",
            "verification_comment", "created_at",
            "updated_at",
        )


class TeacherOnboardingSerializer(serializers.Serializer):
    requested_organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="requested_organization",
        write_only=True,
    )
    requested_department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="requested_department",
        write_only=True,
        allow_null=True,
        required=False,
    )

    public_title = serializers.CharField(required=False, allow_blank=True, max_length=255)
    short_bio = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    education = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.IntegerField(required=False, min_value=0)
    achievements = serializers.CharField(required=False, allow_blank=True)

    position = serializers.CharField(required=False, allow_blank=True, write_only=True)
    employee_code = serializers.CharField(required=False, allow_blank=True, write_only=True)

    is_public = serializers.BooleanField(required=False)
    show_on_teachers_page = serializers.BooleanField(required=False)

    def validate(self, attrs):
        requested_organization = attrs.get("requested_organization")
        requested_department = attrs.get("requested_department")

        if (
            requested_department
            and requested_organization
            and requested_department.organization_id != requested_organization.id
        ):
            raise serializers.ValidationError(
                {"requested_department_id": _("Подразделение должно принадлежать выбранной организации.")}
            )

        return attrs


class TeacherProfileReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = (
            "verification_status",
            "verification_comment",
        )

    def validate_verification_comment(self, value):
        return value.strip()
