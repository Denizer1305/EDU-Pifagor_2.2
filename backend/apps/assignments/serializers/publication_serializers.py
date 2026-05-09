from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import AssignmentPublication


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


def _assignment_payload(assignment):
    if not assignment:
        return None
    return {
        "id": assignment.id,
        "title": getattr(assignment, "title", "") or "",
        "status": getattr(assignment, "status", "") or "",
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


class AssignmentPublicationListSerializer(serializers.ModelSerializer):
    assignment = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()
    published_by = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentPublication
        fields = (
            "id",
            "assignment",
            "course",
            "lesson",
            "published_by",
            "title_override",
            "starts_at",
            "due_at",
            "available_until",
            "status",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        return _assignment_payload(getattr(obj, "assignment", None))

    def get_course(self, obj):
        return _course_payload(getattr(obj, "course", None))

    def get_lesson(self, obj):
        return _lesson_payload(getattr(obj, "lesson", None))

    def get_published_by(self, obj):
        return _user_payload(getattr(obj, "published_by", None))


class AssignmentPublicationDetailSerializer(serializers.ModelSerializer):
    assignment = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    lesson = serializers.SerializerMethodField()
    published_by = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentPublication
        fields = (
            "id",
            "assignment",
            "course",
            "lesson",
            "published_by",
            "title_override",
            "starts_at",
            "due_at",
            "available_until",
            "status",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        return _assignment_payload(getattr(obj, "assignment", None))

    def get_course(self, obj):
        return _course_payload(getattr(obj, "course", None))

    def get_lesson(self, obj):
        return _lesson_payload(getattr(obj, "lesson", None))

    def get_published_by(self, obj):
        return _user_payload(getattr(obj, "published_by", None))


class AssignmentPublicationCreateSerializer(serializers.Serializer):
    assignment_id = serializers.IntegerField()
    course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)
    title_override = serializers.CharField(required=False, allow_blank=True, default="")
    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    available_until = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    is_active = serializers.BooleanField(required=False, default=True)
    status = serializers.CharField(required=False, allow_blank=True, default="")


class AssignmentPublicationUpdateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=False, allow_null=True)
    title_override = serializers.CharField(required=False, allow_blank=True)
    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    available_until = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    status = serializers.CharField(required=False, allow_blank=True)
