from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.course.models import CourseTeacher
from apps.course.serializers.course.short import UserShortSerializer
from apps.course.validators import validate_course_teacher_user

User = get_user_model()


class CourseTeacherSerializer(serializers.ModelSerializer):
    teacher = UserShortSerializer(read_only=True)

    class Meta:
        model = CourseTeacher
        fields = (
            "id",
            "teacher",
            "role",
            "is_active",
            "can_edit",
            "can_manage_structure",
            "can_manage_assignments",
            "can_view_analytics",
            "assigned_at",
            "created_at",
            "updated_at",
        )


class CourseTeacherCreateSerializer(serializers.Serializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.ChoiceField(
        choices=CourseTeacher.RoleChoices.choices,
        default=CourseTeacher.RoleChoices.TEACHER,
    )
    is_active = serializers.BooleanField(default=True)
    can_edit = serializers.BooleanField(default=True)
    can_manage_structure = serializers.BooleanField(default=True)
    can_manage_assignments = serializers.BooleanField(default=False)
    can_view_analytics = serializers.BooleanField(default=True)

    def validate_teacher(self, value):
        validate_course_teacher_user(user=value)
        return value


class CourseTeacherUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=CourseTeacher.RoleChoices.choices,
        required=False,
    )
    is_active = serializers.BooleanField(required=False)
    can_edit = serializers.BooleanField(required=False)
    can_manage_structure = serializers.BooleanField(required=False)
    can_manage_assignments = serializers.BooleanField(required=False)
    can_view_analytics = serializers.BooleanField(required=False)
