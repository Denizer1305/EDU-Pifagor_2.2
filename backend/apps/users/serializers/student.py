from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.organizations.models import Department, Group, Organization
from apps.users.models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    full_name = serializers.CharField(
        source="user.profile.full_name",
        read_only=True,
    )

    class Meta:
        model = StudentProfile
        fields = (
            "id", "user",
            "email", "full_name",
            "student_code", "requested_organization",
            "requested_department", "requested_group",
            "submitted_group_code", "verification_status",
            "verified_by", "verified_at",
            "verification_comment", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "user",
            "email", "full_name",
            "verification_status", "verified_by",
            "verified_at", "verification_comment",
            "created_at", "updated_at",
        )


class StudentOnboardingSerializer(serializers.Serializer):
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
    requested_group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="requested_group",
        write_only=True,
    )
    submitted_group_code = serializers.CharField(
        required=True,
        max_length=128,
        write_only=True,
    )
    admission_year = serializers.IntegerField(
        required=False,
        min_value=1900,
        write_only=True,
    )
    graduation_year = serializers.IntegerField(
        required=False,
        min_value=1900,
        write_only=True,
    )
    student_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=128,
        write_only=True,
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    def validate_student_code(self, value):
        return value.strip()

    def validate_notes(self, value):
        return value.strip()

    def validate_submitted_group_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_("Введите код группы."))
        return value

    def validate(self, attrs):
        requested_organization = attrs.get("requested_organization")
        requested_department = attrs.get("requested_department")
        requested_group = attrs.get("requested_group")
        admission_year = attrs.get("admission_year")
        graduation_year = attrs.get("graduation_year")

        if (
            requested_department
            and requested_organization
            and requested_department.organization_id != requested_organization.id
        ):
            raise serializers.ValidationError(
                {"requested_department_id": _("Отделение должно принадлежать выбранной организации.")}
            )

        if (
            requested_group
            and requested_organization
            and requested_group.organization_id != requested_organization.id
        ):
            raise serializers.ValidationError(
                {"requested_group_id": _("Группа должна принадлежать выбранной организации.")}
            )

        if (
            requested_group
            and requested_department
            and requested_group.department_id
            and requested_group.department_id != requested_department.id
        ):
            raise serializers.ValidationError(
                {"requested_group_id": _("Группа должна принадлежать выбранному отделению.")}
            )

        if (
            admission_year is not None
            and graduation_year is not None
            and graduation_year < admission_year
        ):
            raise serializers.ValidationError(
                {"graduation_year": _("Год выпуска не может быть меньше года поступления.")}
            )

        return attrs


class StudentProfileReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = (
            "verification_status",
            "verification_comment",
        )

    def validate_verification_comment(self, value):
        return value.strip()
