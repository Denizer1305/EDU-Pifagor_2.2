from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.course.models import Course, CourseAssignment, CourseEnrollment
from apps.course.validators import (
    validate_assignment_payload,
    validate_course_student_user,
    validate_enrollment_payload,
)
from apps.organizations.models import Group

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "full_name")

    def get_full_name(self, obj):
        profile = getattr(obj, "profile", None)
        if profile is not None and getattr(profile, "full_name", ""):
            return profile.full_name
        first_name = getattr(profile, "first_name", "") if profile else ""
        last_name = getattr(profile, "last_name", "") if profile else ""
        patronymic = getattr(profile, "patronymic", "") if profile else ""
        parts = [last_name, first_name, patronymic]
        return " ".join(part for part in parts if part).strip() or obj.email


class GroupShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name", "code")


class CourseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "code", "slug", "title", "subtitle", "status")


class CourseAssignmentListSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(read_only=True)
    group = GroupShortSerializer(read_only=True)
    student = UserShortSerializer(read_only=True)
    assigned_by = UserShortSerializer(read_only=True)

    class Meta:
        model = CourseAssignment
        fields = (
            "id",
            "course",
            "assignment_type",
            "group",
            "student",
            "assigned_by",
            "starts_at",
            "ends_at",
            "is_active",
            "auto_enroll",
            "notes",
            "created_at",
            "updated_at",
        )


class CourseAssignmentDetailSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(read_only=True)
    group = GroupShortSerializer(read_only=True)
    student = UserShortSerializer(read_only=True)
    assigned_by = UserShortSerializer(read_only=True)

    class Meta:
        model = CourseAssignment
        fields = (
            "id",
            "course",
            "assignment_type",
            "group",
            "student",
            "assigned_by",
            "starts_at",
            "ends_at",
            "is_active",
            "auto_enroll",
            "notes",
            "created_at",
            "updated_at",
        )


class CourseAssignmentCreateSerializer(serializers.Serializer):
    assignment_type = serializers.ChoiceField(choices=CourseAssignment.AssignmentTypeChoices.choices)
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    starts_at = serializers.DateTimeField(required=False, allow_null=True, default=None)
    ends_at = serializers.DateTimeField(required=False, allow_null=True, default=None)
    is_active = serializers.BooleanField(default=True)
    auto_enroll = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_student(self, value):
        if value is not None:
            validate_course_student_user(user=value)
        return value

    def validate(self, attrs):
        validate_assignment_payload(
            assignment_type=attrs.get("assignment_type"),
            group=attrs.get("group"),
            student=attrs.get("student"),
            starts_at=attrs.get("starts_at"),
            ends_at=attrs.get("ends_at"),
        )
        return attrs


class CourseAssignmentUpdateSerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    auto_enroll = serializers.BooleanField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        assignment = self.instance
        validate_assignment_payload(
            assignment_type=assignment.assignment_type,
            group=assignment.group,
            student=assignment.student,
            starts_at=attrs.get("starts_at", assignment.starts_at),
            ends_at=attrs.get("ends_at", assignment.ends_at),
        )
        return attrs


class CourseEnrollmentListSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(read_only=True)
    student = UserShortSerializer(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = (
            "id",
            "course",
            "student",
            "status",
            "progress_percent",
            "enrolled_at",
            "started_at",
            "completed_at",
            "last_activity_at",
            "created_at",
            "updated_at",
        )


class CourseEnrollmentDetailSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(read_only=True)
    student = UserShortSerializer(read_only=True)
    assignment = CourseAssignmentDetailSerializer(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = (
            "id",
            "course",
            "student",
            "assignment",
            "status",
            "progress_percent",
            "enrolled_at",
            "started_at",
            "completed_at",
            "last_activity_at",
            "created_at",
            "updated_at",
        )


class CourseEnrollmentCreateSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    assignment = serializers.PrimaryKeyRelatedField(
        queryset=CourseAssignment.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    status = serializers.ChoiceField(
        choices=CourseEnrollment.StatusChoices.choices,
        default=CourseEnrollment.StatusChoices.ENROLLED,
    )

    def validate_student(self, value):
        validate_course_student_user(user=value)
        return value

    def validate(self, attrs):
        course = self.context.get("course")
        if course is None:
            raise serializers.ValidationError({"course": "Курс не передан в контекст сериализатора."})

        validate_enrollment_payload(
            course=course,
            student=attrs["student"],
            assignment=attrs.get("assignment"),
        )
        return attrs
