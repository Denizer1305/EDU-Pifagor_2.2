from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import SubmissionAttachment
from apps.assignments.serializers.assignment_structure import (
    AssignmentQuestionSerializer,
)
from apps.assignments.serializers.submission_serializers.common import build_file_url


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
        return build_file_url(getattr(obj, "file", None), self.context)

    def get_question(self, obj):
        question = getattr(obj, "question", None)
        if not question:
            return None

        return AssignmentQuestionSerializer(
            question,
            context=self.context,
        ).data
