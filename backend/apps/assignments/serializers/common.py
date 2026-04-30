from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.assignments.models import Assignment, AssignmentPublication

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
        )

    def get_full_name(self, obj) -> str:
        profile = getattr(obj, "profile", None)
        if profile is None:
            return obj.email or f"Пользователь #{obj.pk}"

        parts = [
            getattr(profile, "last_name", ""),
            getattr(profile, "first_name", ""),
            getattr(profile, "patronymic", ""),
        ]
        value = " ".join(part for part in parts if part).strip()
        return value or obj.email or f"Пользователь #{obj.pk}"


class CourseBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)


class LessonBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(required=False)


class SubjectBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OrganizationBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class GroupBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    code = serializers.CharField(required=False, allow_blank=True)


class CourseEnrollmentBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_id = serializers.IntegerField(required=False)
    student_id = serializers.IntegerField(required=False)
    status = serializers.CharField(required=False, allow_blank=True)


class AssignmentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "uid",
            "title",
            "assignment_kind",
            "status",
            "visibility",
            "education_level",
        )


class AssignmentPublicationBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentPublication
        fields = (
            "id",
            "status",
            "starts_at",
            "due_at",
            "available_until",
            "is_active",
        )
