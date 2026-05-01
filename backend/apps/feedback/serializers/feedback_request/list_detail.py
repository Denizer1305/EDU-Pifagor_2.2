from __future__ import annotations

from apps.feedback.serializers.feedback_attachment import FeedbackAttachmentSerializer
from apps.feedback.serializers.feedback_request.base import FeedbackRequestBaseSerializer
from apps.feedback.serializers.feedback_request.related import (
    FeedbackRequestContactSerializer,
    FeedbackRequestProcessingSerializer,
    FeedbackRequestTechnicalSerializer,
    FeedbackStatusHistorySerializer,
)


class FeedbackRequestListSerializer(FeedbackRequestBaseSerializer):
    class Meta(FeedbackRequestBaseSerializer.Meta):
        fields = (
            "id",
            "uid",
            "type",
            "type_display",
            "status",
            "status_display",
            "source",
            "source_display",
            "subject",
            "sender_display",
            "full_name",
            "email",
            "phone",
            "organization_name",
            "attachments_count",
            "is_personal_data_consent",
            "is_processed",
            "is_spam_suspected",
            "created_at",
        )
        read_only_fields = fields


class FeedbackRequestDetailSerializer(FeedbackRequestBaseSerializer):
    attachments = FeedbackAttachmentSerializer(many=True, read_only=True)
    contact = FeedbackRequestContactSerializer(read_only=True)
    technical = FeedbackRequestTechnicalSerializer(read_only=True)
    processing = FeedbackRequestProcessingSerializer(read_only=True)
    status_history = FeedbackStatusHistorySerializer(many=True, read_only=True)

    class Meta(FeedbackRequestBaseSerializer.Meta):
        fields = FeedbackRequestBaseSerializer.Meta.fields + (
            "attachments",
            "contact",
            "technical",
            "processing",
            "status_history",
        )
        read_only_fields = fields
