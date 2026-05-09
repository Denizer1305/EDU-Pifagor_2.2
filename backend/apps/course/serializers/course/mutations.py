from __future__ import annotations

from rest_framework import serializers

from apps.course.models import Course
from apps.course.validators import (
    validate_course_can_be_published,
    validate_course_dates,
)
from apps.education.models import AcademicYear, EducationPeriod, GroupSubject
from apps.organizations.models import Organization, Subject


class CourseCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    course_type = serializers.ChoiceField(
        choices=Course.CourseTypeChoices.choices,
        default=Course.CourseTypeChoices.AUTHOR,
    )
    origin = serializers.ChoiceField(
        choices=Course.OriginChoices.choices,
        default=Course.OriginChoices.MANUAL,
    )
    status = serializers.ChoiceField(
        choices=Course.StatusChoices.choices,
        required=False,
        default=Course.StatusChoices.DRAFT,
    )
    visibility = serializers.ChoiceField(
        choices=Course.VisibilityChoices.choices,
        default=Course.VisibilityChoices.ASSIGNED_ONLY,
    )
    level = serializers.ChoiceField(
        choices=Course.LevelChoices.choices,
        default=Course.LevelChoices.BASIC,
    )
    language = serializers.CharField(
        max_length=12,
        required=False,
        allow_blank=True,
        default="ru",
    )

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    group_subject = serializers.PrimaryKeyRelatedField(
        queryset=GroupSubject.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )

    cover_image = serializers.ImageField(
        required=False,
        allow_null=True,
        default=None,
    )
    is_template = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    allow_self_enrollment = serializers.BooleanField(default=False)
    enrollment_code = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    estimated_minutes = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )

    starts_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
    )
    ends_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
    )

    def validate(self, attrs):
        validate_course_dates(
            starts_at=attrs.get("starts_at"),
            ends_at=attrs.get("ends_at"),
        )

        if attrs.get("status") == Course.StatusChoices.PUBLISHED:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Курс нельзя создать сразу опубликованным. "
                        "Сначала добавьте структуру, затем опубликуйте его отдельным действием."
                    )
                }
            )

        return attrs


class CourseUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    subtitle = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    description = serializers.CharField(required=False, allow_blank=True)

    course_type = serializers.ChoiceField(
        choices=Course.CourseTypeChoices.choices,
        required=False,
    )
    origin = serializers.ChoiceField(
        choices=Course.OriginChoices.choices,
        required=False,
    )
    status = serializers.ChoiceField(
        choices=Course.StatusChoices.choices,
        required=False,
    )
    visibility = serializers.ChoiceField(
        choices=Course.VisibilityChoices.choices,
        required=False,
    )
    level = serializers.ChoiceField(
        choices=Course.LevelChoices.choices,
        required=False,
    )
    language = serializers.CharField(
        max_length=12,
        required=False,
        allow_blank=True,
    )

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        required=False,
        allow_null=True,
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        required=False,
        allow_null=True,
    )
    group_subject = serializers.PrimaryKeyRelatedField(
        queryset=GroupSubject.objects.all(),
        required=False,
        allow_null=True,
    )

    cover_image = serializers.ImageField(required=False, allow_null=True)
    is_template = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    allow_self_enrollment = serializers.BooleanField(required=False)
    enrollment_code = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    estimated_minutes = serializers.IntegerField(
        required=False,
        min_value=0,
    )

    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        course = self.context.get("course")

        starts_at = attrs.get("starts_at", getattr(course, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(course, "ends_at", None))

        validate_course_dates(
            starts_at=starts_at,
            ends_at=ends_at,
        )

        status_value = attrs.get("status")
        if status_value == Course.StatusChoices.PUBLISHED:
            if course is not None:
                validate_course_can_be_published(course=course)
            else:
                raise serializers.ValidationError(
                    {"status": "Для публикации используйте отдельное действие."}
                )

        if status_value == Course.StatusChoices.ARCHIVED:
            raise serializers.ValidationError(
                {"status": "Для архивации используйте отдельное действие."}
            )

        return attrs


class CourseDuplicateSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    duplicate_teachers = serializers.BooleanField(default=False)
    duplicate_materials = serializers.BooleanField(default=True)
