from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import ParentProfile, ParentStudent

User = get_user_model()


class ParentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.profile.full_name", read_only=True)

    class Meta:
        model = ParentProfile
        fields = (
            "id",
            "user",
            "email",
            "full_name",
            "occupation",
            "work_place",
            "emergency_contact_phone",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "email",
            "full_name",
            "created_at",
            "updated_at",
        )


class ParentProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = (
            "occupation",
            "work_place",
            "emergency_contact_phone",
            "notes",
        )

    def validate_occupation(self, value):
        return value.strip()

    def validate_work_place(self, value):
        return value.strip()

    def validate_emergency_contact_phone(self, value):
        return value.strip()

    def validate_notes(self, value):
        return value.strip()


class ParentStudentSerializer(serializers.ModelSerializer):
    parent_email = serializers.EmailField(source="parent.email", read_only=True)
    parent_full_name = serializers.CharField(
        source="parent.profile.full_name", read_only=True
    )
    student_email = serializers.EmailField(source="student.email", read_only=True)
    student_full_name = serializers.CharField(
        source="student.profile.full_name", read_only=True
    )

    class Meta:
        model = ParentStudent
        fields = (
            "id",
            "parent",
            "parent_email",
            "parent_full_name",
            "student",
            "student_email",
            "student_full_name",
            "relation_type",
            "status",
            "requested_by",
            "approved_by",
            "approved_at",
            "comment",
            "created_at",
        )
        read_only_fields = (
            "id",
            "parent",
            "parent_email",
            "parent_full_name",
            "student_email",
            "student_full_name",
            "status",
            "requested_by",
            "approved_by",
            "approved_at",
            "created_at",
        )


class ParentStudentRequestSerializer(serializers.Serializer):
    student_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.select_related("profile").all(),
        source="student_user",
        write_only=True,
    )
    relation_type = serializers.CharField(required=True, max_length=32)
    comment = serializers.CharField(required=False, allow_blank=True)
    is_primary = serializers.BooleanField(required=False, default=False)

    def validate_comment(self, value):
        return value.strip()


class ParentStudentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=ParentStudent.LinkStatusChoices.choices,
        required=True,
    )
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate_comment(self, value):
        return value.strip()
