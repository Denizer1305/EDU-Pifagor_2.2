from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import Submission
from apps.assignments.serializers.assignment_structure import (
    AssignmentVariantSerializer,
)
from apps.assignments.serializers.submission_serializers.answers import (
    SubmissionAnswerSerializer,
)
from apps.assignments.serializers.submission_serializers.attachments import (
    SubmissionAttachmentSerializer,
)
from apps.assignments.serializers.submission_serializers.attempts import (
    SubmissionAttemptSerializer,
)
from apps.assignments.serializers.submission_serializers.common import (
    assignment_payload,
    publication_payload,
    user_payload,
)


class SubmissionListSerializer(serializers.ModelSerializer):
    assignment = serializers.SerializerMethodField()
    publication = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    variant = AssignmentVariantSerializer(read_only=True)
    checked_by = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            "id",
            "publication",
            "assignment",
            "variant",
            "student",
            "status",
            "attempt_number",
            "started_at",
            "submitted_at",
            "completed_at",
            "time_spent_minutes",
            "is_late",
            "late_minutes",
            "auto_score",
            "manual_score",
            "final_score",
            "percentage",
            "passed",
            "checked_at",
            "checked_by",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        return assignment_payload(getattr(obj, "assignment", None))

    def get_publication(self, obj):
        return publication_payload(getattr(obj, "publication", None))

    def get_student(self, obj):
        return user_payload(getattr(obj, "student", None))

    def get_checked_by(self, obj):
        return user_payload(getattr(obj, "checked_by", None))


class SubmissionDetailSerializer(serializers.ModelSerializer):
    assignment = serializers.SerializerMethodField()
    publication = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    variant = AssignmentVariantSerializer(read_only=True)
    checked_by = serializers.SerializerMethodField()
    answers = SubmissionAnswerSerializer(many=True, read_only=True)
    attachments = SubmissionAttachmentSerializer(many=True, read_only=True)
    attempts = SubmissionAttemptSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = (
            "id",
            "publication",
            "assignment",
            "variant",
            "student",
            "status",
            "attempt_number",
            "started_at",
            "submitted_at",
            "completed_at",
            "time_spent_minutes",
            "is_late",
            "late_minutes",
            "auto_score",
            "manual_score",
            "final_score",
            "percentage",
            "passed",
            "checked_at",
            "checked_by",
            "answers",
            "attachments",
            "attempts",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        return assignment_payload(getattr(obj, "assignment", None))

    def get_publication(self, obj):
        return publication_payload(getattr(obj, "publication", None))

    def get_student(self, obj):
        return user_payload(getattr(obj, "student", None))

    def get_checked_by(self, obj):
        return user_payload(getattr(obj, "checked_by", None))
