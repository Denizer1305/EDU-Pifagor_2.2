from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import Assignment


def _user_payload(user):
    if not user:
        return None
    return {
        "id": user.id,
        "email": getattr(user, "email", ""),
        "full_name": (
            getattr(user, "get_full_name", lambda: "")() or getattr(user, "email", "")
        ),
    }


def _course_payload(course):
    if not course:
        return None
    return {
        "id": course.id,
        "title": getattr(course, "title", "") or "",
        "slug": getattr(course, "slug", "") or "",
    }


def _lesson_payload(lesson):
    if not lesson:
        return None
    return {
        "id": lesson.id,
        "title": getattr(lesson, "title", "") or "",
        "order": getattr(lesson, "order", 0) or 0,
    }


class AssignmentListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            "id",
            "uid",
            "title",
            "subtitle",
            "assignment_kind",
            "control_scope",
            "status",
            "visibility",
            "education_level",
            "is_template",
            "is_active",
            "author",
            "course",
            "lesson",
            "created_at",
            "updated_at",
        )

    def get_author(self, obj):
        return _user_payload(getattr(obj, "author", None))

    def get_course(self, obj):
        return _course_payload(getattr(obj, "course", None))

    def get_lesson(self, obj):
        return _lesson_payload(getattr(obj, "lesson", None))


class AssignmentDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            "id",
            "uid",
            "title",
            "subtitle",
            "description",
            "instructions",
            "assignment_kind",
            "control_scope",
            "status",
            "visibility",
            "education_level",
            "is_template",
            "is_active",
            "author",
            "course",
            "lesson",
            "created_at",
            "updated_at",
        )

    def get_author(self, obj):
        return _user_payload(getattr(obj, "author", None))

    def get_course(self, obj):
        return _course_payload(getattr(obj, "course", None))

    def get_lesson(self, obj):
        return _lesson_payload(getattr(obj, "lesson", None))


class AssignmentCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    instructions = serializers.CharField(required=False, allow_blank=True, default="")
    assignment_kind = serializers.CharField(required=False, allow_blank=True, default="")
    control_scope = serializers.CharField(required=False, allow_blank=True, default="")
    visibility = serializers.CharField(required=False, allow_blank=True, default="")
    education_level = serializers.CharField(required=False, allow_blank=True, default="")
    is_template = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)
    course_id = serializers.IntegerField(required=False)
    lesson_id = serializers.IntegerField(required=False)

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Название обязательно.")
        return value


class AssignmentUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=255)
    subtitle = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    instructions = serializers.CharField(required=False, allow_blank=True)
    assignment_kind = serializers.CharField(required=False, allow_blank=True)
    control_scope = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.CharField(required=False, allow_blank=True)
    education_level = serializers.CharField(required=False, allow_blank=True)
    is_template = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)


class AssignmentDuplicateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=False, max_length=255)
