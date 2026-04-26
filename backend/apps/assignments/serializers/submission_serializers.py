from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import (
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
)
from apps.assignments.serializers.assignment_structure import (
    AssignmentQuestionSerializer,
    AssignmentVariantSerializer,
)


def _user_payload(user):
    if not user:
        return None

    full_name = ""
    if hasattr(user, "get_full_name"):
        full_name = user.get_full_name() or ""

    return {
        "id": user.id,
        "email": getattr(user, "email", "") or "",
        "full_name": full_name or getattr(user, "email", "") or "",
    }


def _assignment_payload(assignment):
    if not assignment:
        return None

    return {
        "id": assignment.id,
        "title": getattr(assignment, "title", "") or "",
        "status": getattr(assignment, "status", "") or "",
        "assignment_kind": getattr(assignment, "assignment_kind", "") or "",
    }


def _publication_payload(publication):
    if not publication:
        return None

    return {
        "id": publication.id,
        "title_override": getattr(publication, "title_override", "") or "",
        "status": getattr(publication, "status", "") or "",
        "starts_at": getattr(publication, "starts_at", None),
        "due_at": getattr(publication, "due_at", None),
        "available_until": getattr(publication, "available_until", None),
    }


class SubmissionAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    question = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionAttachment
        fields = (
            "id",
            "question",
            "file",
            "file_url",
            "original_name",
            "mime_type",
            "file_size",
            "attachment_type",
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj):
        if not getattr(obj, "file", None):
            return ""

        request = self.context.get("request")
        try:
            url = obj.file.url
        except Exception:
            return ""

        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def get_question(self, obj):
        question = getattr(obj, "question", None)
        if not question:
            return None
        return AssignmentQuestionSerializer(
            question,
            context=self.context,
        ).data


class SubmissionAnswerSerializer(serializers.ModelSerializer):
    question = AssignmentQuestionSerializer(read_only=True)

    class Meta:
        model = SubmissionAnswer
        fields = (
            "id",
            "question",
            "answer_text",
            "answer_json",
            "selected_options_json",
            "numeric_answer",
            "is_correct",
            "auto_score",
            "manual_score",
            "final_score",
            "review_status",
            "created_at",
            "updated_at",
        )


class SubmissionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionAttempt
        fields = (
            "id",
            "attempt_number",
            "started_at",
            "submitted_at",
            "time_spent_minutes",
            "status",
            "snapshot_json",
            "created_at",
            "updated_at",
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
        return _assignment_payload(getattr(obj, "assignment", None))

    def get_publication(self, obj):
        return _publication_payload(getattr(obj, "publication", None))

    def get_student(self, obj):
        return _user_payload(getattr(obj, "student", None))

    def get_checked_by(self, obj):
        return _user_payload(getattr(obj, "checked_by", None))


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
        return _assignment_payload(getattr(obj, "assignment", None))

    def get_publication(self, obj):
        return _publication_payload(getattr(obj, "publication", None))

    def get_student(self, obj):
        return _user_payload(getattr(obj, "student", None))

    def get_checked_by(self, obj):
        return _user_payload(getattr(obj, "checked_by", None))


class SubmissionStartSerializer(serializers.Serializer):
    publication_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)


class SubmissionAnswerSaveSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    answer_json = serializers.JSONField(required=False, allow_null=True)
    selected_options_json = serializers.JSONField(required=False, allow_null=True)
    numeric_answer = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class SubmissionAttachFileSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    file = serializers.FileField()


class SubmissionSubmitSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(required=False, default=True)


class SubmissionRetrySerializer(serializers.Serializer):
    confirm = serializers.BooleanField(required=False, default=True)
