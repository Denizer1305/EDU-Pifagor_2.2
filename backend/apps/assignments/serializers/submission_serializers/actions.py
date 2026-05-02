from __future__ import annotations

from rest_framework import serializers


class SubmissionStartSerializer(serializers.Serializer):
    publication_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)


class SubmissionAnswerSaveSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
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
