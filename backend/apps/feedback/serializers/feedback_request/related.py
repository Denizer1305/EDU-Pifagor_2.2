from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import (
    FeedbackRequest,
    FeedbackRequestContact,
    FeedbackRequestProcessing,
    FeedbackRequestTechnical,
    FeedbackStatusHistory,
)


class FeedbackRequestContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackRequestContact
        fields = (
            "full_name",
            "email",
            "phone",
            "organization_name",
        )
        read_only_fields = fields


class FeedbackRequestTechnicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackRequestTechnical
        fields = (
            "page_url",
            "frontend_route",
            "error_code",
            "error_title",
            "error_details",
            "client_platform",
            "app_version",
            "ip_address",
            "user_agent",
            "referrer",
            "extra_payload",
        )
        read_only_fields = fields


class FeedbackRequestProcessingSerializer(serializers.ModelSerializer):
    assigned_to_email = serializers.SerializerMethodField(read_only=True)
    processed_by_email = serializers.SerializerMethodField(read_only=True)
    is_processed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedbackRequestProcessing
        fields = (
            "assigned_to",
            "assigned_to_email",
            "assigned_at",
            "processed_by",
            "processed_by_email",
            "processed_at",
            "is_processed",
            "reply_message",
            "internal_note",
            "is_spam_suspected",
        )
        read_only_fields = fields

    def get_assigned_to_email(self, obj: FeedbackRequestProcessing) -> str:
        if obj.assigned_to_id:
            return obj.assigned_to.email

        return ""

    def get_processed_by_email(self, obj: FeedbackRequestProcessing) -> str:
        if obj.processed_by_id:
            return obj.processed_by.email

        return ""

    def get_is_processed(self, obj: FeedbackRequestProcessing) -> bool:
        return obj.is_processed


class FeedbackStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.SerializerMethodField(read_only=True)
    from_status_display = serializers.SerializerMethodField(read_only=True)
    to_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedbackStatusHistory
        fields = (
            "id",
            "from_status",
            "from_status_display",
            "to_status",
            "to_status_display",
            "comment",
            "changed_by",
            "changed_by_email",
            "created_at",
        )
        read_only_fields = fields

    def _get_status_display(self, value: str) -> str:
        if not value:
            return ""

        try:
            return FeedbackRequest.StatusChoices(value).label
        except ValueError:
            return value

    def get_changed_by_email(self, obj: FeedbackStatusHistory) -> str:
        if obj.changed_by_id:
            return obj.changed_by.email

        return ""

    def get_from_status_display(self, obj: FeedbackStatusHistory) -> str:
        return self._get_status_display(obj.from_status)

    def get_to_status_display(self, obj: FeedbackStatusHistory) -> str:
        return self._get_status_display(obj.to_status)
