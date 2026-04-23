from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models import ParentProfile, StudentProfile, TeacherProfile, UserRole
from apps.users.serializers.profile import ProfileDetailSerializer
from apps.users.serializers.role import UserRoleSerializer

User = get_user_model()


def _user_role_queryset(obj):
    queryset = obj.user_roles.select_related("role")
    model_fields = {field.name for field in UserRole._meta.get_fields()}
    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)
    return queryset


class TeacherProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = (
            "id", "public_title",
            "short_bio", "is_public",
            "show_on_teachers_page",
            "requested_organization", "requested_department",
            "verification_status", "code_verified_at",
            "verified_at",
        )
        read_only_fields = fields


class StudentProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = (
            "id", "student_code",
            "requested_organization",
            "requested_department", "requested_group",
            "verification_status", "verified_at",
        )
        read_only_fields = fields


class ParentProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = (
            "id", "occupation",
            "work_place", "created_at",
        )
        read_only_fields = fields


class CurrentUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    teacher_profile = serializers.SerializerMethodField()
    student_profile = serializers.SerializerMethodField()
    parent_profile = serializers.SerializerMethodField()
    reviewed_by_id = serializers.IntegerField(source="reviewed_by.id", read_only=True)
    reviewed_by_email = serializers.EmailField(
        source="reviewed_by.email",
        read_only=True,
        default=None,
    )
    is_email_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email",
            "registration_type", "onboarding_status",
            "onboarding_completed_at", "is_email_verified",
            "is_active", "reviewed_by_id",
            "reviewed_by_email", "reviewed_at",
            "review_comment", "profile",
            "roles", "teacher_profile",
            "student_profile", "parent_profile",
            "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_is_email_verified(self, obj):
        if hasattr(obj, "is_email_verified"):
            return obj.is_email_verified
        return False

    def get_profile(self, obj):
        if hasattr(obj, "profile"):
            return ProfileDetailSerializer(obj.profile).data
        return None

    def get_roles(self, obj):
        return UserRoleSerializer(_user_role_queryset(obj), many=True).data

    def get_teacher_profile(self, obj):
        if hasattr(obj, "teacher_profile"):
            return TeacherProfileShortSerializer(obj.teacher_profile).data
        return None

    def get_student_profile(self, obj):
        if hasattr(obj, "student_profile"):
            return StudentProfileShortSerializer(obj.student_profile).data
        return None

    def get_parent_profile(self, obj):
        if hasattr(obj, "parent_profile"):
            return ParentProfileShortSerializer(obj.parent_profile).data
        return None
