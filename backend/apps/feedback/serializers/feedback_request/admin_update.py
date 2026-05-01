from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import FeedbackRequest


class FeedbackRequestAdminUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=FeedbackRequest.StatusChoices.choices,
        required=False,
    )
    reply_message = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    internal_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    is_spam_suspected = serializers.BooleanField(required=False)
    is_processed = serializers.BooleanField(required=False)

    def validate(self, attrs):
        status_value = attrs.get("status")
        is_processed = attrs.get("is_processed")

        if (
            status_value == FeedbackRequest.StatusChoices.RESOLVED
            and is_processed is False
        ):
            raise serializers.ValidationError(
                {
                    "is_processed": (
                        "Решённое обращение не может быть не обработанным."
                    )
                }
            )

        if (
            status_value == FeedbackRequest.StatusChoices.SPAM
            and attrs.get("is_spam_suspected") is False
        ):
            raise serializers.ValidationError(
                {
                    "is_spam_suspected": (
                        "Обращение со статусом 'Спам' не может иметь "
                        "отрицательный флаг спама."
                    )
                }
            )

        return attrs
