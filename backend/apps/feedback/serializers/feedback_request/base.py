from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import FeedbackRequest


class FeedbackRequestBaseSerializer(serializers.ModelSerializer):
    attachments_count = serializers.SerializerMethodField(read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_display = serializers.CharField(source="get_source_display", read_only=True)

    sender_display = serializers.SerializerMethodField(read_only=True)

    full_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    organization_name = serializers.SerializerMethodField(read_only=True)

    page_url = serializers.SerializerMethodField(read_only=True)
    frontend_route = serializers.SerializerMethodField(read_only=True)
    error_code = serializers.SerializerMethodField(read_only=True)
    error_title = serializers.SerializerMethodField(read_only=True)
    error_details = serializers.SerializerMethodField(read_only=True)
    client_platform = serializers.SerializerMethodField(read_only=True)
    app_version = serializers.SerializerMethodField(read_only=True)
    ip_address = serializers.SerializerMethodField(read_only=True)
    user_agent = serializers.SerializerMethodField(read_only=True)
    referrer = serializers.SerializerMethodField(read_only=True)

    is_processed = serializers.SerializerMethodField(read_only=True)
    processed_at = serializers.SerializerMethodField(read_only=True)
    processed_by = serializers.SerializerMethodField(read_only=True)
    processed_by_email = serializers.SerializerMethodField(read_only=True)
    assigned_to = serializers.SerializerMethodField(read_only=True)
    assigned_to_email = serializers.SerializerMethodField(read_only=True)
    assigned_at = serializers.SerializerMethodField(read_only=True)
    reply_message = serializers.SerializerMethodField(read_only=True)
    internal_note = serializers.SerializerMethodField(read_only=True)
    is_spam_suspected = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedbackRequest
        fields = (
            "id",
            "uid",
            "user",
            "type",
            "type_display",
            "status",
            "status_display",
            "source",
            "source_display",
            "subject",
            "message",
            "sender_display",
            "full_name",
            "email",
            "phone",
            "organization_name",
            "is_personal_data_consent",
            "personal_data_consent_at",
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
            "is_processed",
            "processed_at",
            "processed_by",
            "processed_by_email",
            "assigned_to",
            "assigned_to_email",
            "assigned_at",
            "reply_message",
            "internal_note",
            "is_spam_suspected",
            "attachments_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def _get_contact(self, obj: FeedbackRequest):
        return getattr(obj, "contact", None)

    def _get_technical(self, obj: FeedbackRequest):
        return getattr(obj, "technical", None)

    def _get_processing(self, obj: FeedbackRequest):
        return getattr(obj, "processing", None)

    def get_attachments_count(self, obj: FeedbackRequest) -> int:
        prefetched = getattr(obj, "attachments", None)

        if prefetched is not None and hasattr(prefetched, "all"):
            return prefetched.count()

        return obj.attachments.count()

    def get_sender_display(self, obj: FeedbackRequest) -> str:
        contact = self._get_contact(obj)

        if contact and contact.full_name:
            return contact.full_name

        if obj.user_id:
            return getattr(obj.user, "email", "—")

        if contact and contact.email:
            return contact.email

        return "—"

    def get_full_name(self, obj: FeedbackRequest) -> str:
        contact = self._get_contact(obj)
        return contact.full_name if contact else ""

    def get_email(self, obj: FeedbackRequest) -> str:
        contact = self._get_contact(obj)

        if contact and contact.email:
            return contact.email

        if obj.user_id:
            return getattr(obj.user, "email", "")

        return ""

    def get_phone(self, obj: FeedbackRequest) -> str:
        contact = self._get_contact(obj)
        return contact.phone if contact else ""

    def get_organization_name(self, obj: FeedbackRequest) -> str:
        contact = self._get_contact(obj)
        return contact.organization_name if contact else ""

    def get_page_url(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.page_url if technical else ""

    def get_frontend_route(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.frontend_route if technical else ""

    def get_error_code(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.error_code if technical else ""

    def get_error_title(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.error_title if technical else ""

    def get_error_details(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.error_details if technical else ""

    def get_client_platform(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.client_platform if technical else ""

    def get_app_version(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.app_version if technical else ""

    def get_ip_address(self, obj: FeedbackRequest):
        technical = self._get_technical(obj)
        return technical.ip_address if technical else None

    def get_user_agent(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.user_agent if technical else ""

    def get_referrer(self, obj: FeedbackRequest) -> str:
        technical = self._get_technical(obj)
        return technical.referrer if technical else ""

    def get_is_processed(self, obj: FeedbackRequest) -> bool:
        processing = self._get_processing(obj)
        return bool(processing and processing.processed_at)

    def get_processed_at(self, obj: FeedbackRequest):
        processing = self._get_processing(obj)
        return processing.processed_at if processing else None

    def get_processed_by(self, obj: FeedbackRequest):
        processing = self._get_processing(obj)
        return processing.processed_by_id if processing else None

    def get_processed_by_email(self, obj: FeedbackRequest) -> str:
        processing = self._get_processing(obj)

        if processing and processing.processed_by_id:
            return processing.processed_by.email

        return ""

    def get_assigned_to(self, obj: FeedbackRequest):
        processing = self._get_processing(obj)
        return processing.assigned_to_id if processing else None

    def get_assigned_to_email(self, obj: FeedbackRequest) -> str:
        processing = self._get_processing(obj)

        if processing and processing.assigned_to_id:
            return processing.assigned_to.email

        return ""

    def get_assigned_at(self, obj: FeedbackRequest):
        processing = self._get_processing(obj)
        return processing.assigned_at if processing else None

    def get_reply_message(self, obj: FeedbackRequest) -> str:
        processing = self._get_processing(obj)
        return processing.reply_message if processing else ""

    def get_internal_note(self, obj: FeedbackRequest) -> str:
        processing = self._get_processing(obj)
        return processing.internal_note if processing else ""

    def get_is_spam_suspected(self, obj: FeedbackRequest) -> bool:
        processing = self._get_processing(obj)
        return bool(processing and processing.is_spam_suspected)
