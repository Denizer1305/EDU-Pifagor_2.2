from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import SubmissionAnswer
from apps.assignments.serializers.assignment_structure import AssignmentQuestionSerializer


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
