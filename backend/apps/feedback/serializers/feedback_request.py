from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import (
    FeedbackRequest,
    FeedbackRequestContact,
    FeedbackRequestProcessing,
    FeedbackRequestTechnical,
    FeedbackStatusHistory,
)
from apps.feedback.serializers.feedback_attachment import FeedbackAttachmentSerializer
from apps.feedback.services.feedback_services import MAX_ATTACHMENTS_PER_REQUEST


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


class FeedbackRequestCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=FeedbackRequest.TypeChoices.choices,
        default=FeedbackRequest.TypeChoices.QUESTION,
    )
    subject = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    message = serializers.CharField()
    full_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=32,
    )
    organization_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    is_personal_data_consent = serializers.BooleanField()
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    def validate_message(self, value: str) -> str:
        value = (value or "").strip()
        if len(value) < 5:
            raise serializers.ValidationError(
                "Сообщение должно содержать не менее 5 символов."
            )
        return value

    def validate_subject(self, value: str) -> str:
        return (value or "").strip()

    def validate_full_name(self, value: str) -> str:
        return (value or "").strip()

    def validate_phone(self, value: str) -> str:
        return (value or "").strip()

    def validate_organization_name(self, value: str) -> str:
        return (value or "").strip()

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        email = (attrs.get("email") or "").strip()
        is_consent = attrs.get("is_personal_data_consent", False)

        if not is_consent:
            raise serializers.ValidationError(
                {
                    "is_personal_data_consent": (
                        "Необходимо согласие на обработку персональных данных."
                    )
                }
            )

        if not email and not (user and user.is_authenticated):
            raise serializers.ValidationError(
                {
                    "email": (
                        "Для неавторизованного пользователя email обязателен."
                    )
                }
            )

        attachments = attrs.get("attachments") or []
        if len(attachments) > MAX_ATTACHMENTS_PER_REQUEST:
            raise serializers.ValidationError(
                {
                    "attachments": (
                        f"Можно прикрепить не более {MAX_ATTACHMENTS_PER_REQUEST} файлов."
                    )
                }
            )

        return attrs


class FeedbackRequestErrorCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=FeedbackRequest.TypeChoices.choices,
        default=FeedbackRequest.TypeChoices.BUG,
    )
    subject = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    message = serializers.CharField()
    is_personal_data_consent = serializers.BooleanField()

    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    page_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    frontend_route = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    error_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    error_title = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    error_details = serializers.CharField(
        required=False,
        allow_blank=True,
        style={"base_template": "textarea.html"},
    )
    client_platform = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    app_version = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )

    def validate_message(self, value: str) -> str:
        value = (value or "").strip()
        if len(value) < 5:
            raise serializers.ValidationError(
                "Сообщение должно содержать не менее 5 символов."
            )
        return value

    def validate_subject(self, value: str) -> str:
        return (value or "").strip()

    def validate_frontend_route(self, value: str) -> str:
        return (value or "").strip()

    def validate_error_code(self, value: str) -> str:
        return (value or "").strip()

    def validate_error_title(self, value: str) -> str:
        return (value or "").strip()

    def validate_error_details(self, value: str) -> str:
        value = (value or "").strip()
        if len(value) > 10000:
            raise serializers.ValidationError(
                "Технические детали ошибки не должны превышать 10000 символов."
            )
        return value

    def validate_client_platform(self, value: str) -> str:
        return (value or "").strip()

    def validate_app_version(self, value: str) -> str:
        return (value or "").strip()

    def validate(self, attrs):
        is_consent = attrs.get("is_personal_data_consent", False)
        if not is_consent:
            raise serializers.ValidationError(
                {
                    "is_personal_data_consent": (
                        "Необходимо согласие на обработку персональных данных."
                    )
                }
            )

        attachments = attrs.get("attachments") or []
        if len(attachments) > MAX_ATTACHMENTS_PER_REQUEST:
            raise serializers.ValidationError(
                {
                    "attachments": (
                        f"Можно прикрепить не более {MAX_ATTACHMENTS_PER_REQUEST} файлов."
                    )
                }
            )

        if not attrs.get("subject") and attrs.get("error_title"):
            attrs["subject"] = attrs["error_title"]

        return attrs


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

        if status_value == FeedbackRequest.StatusChoices.RESOLVED and is_processed is False:
            raise serializers.ValidationError(
                {
                    "is_processed": (
                        "Решённое обращение не может быть не обработанным."
                    )
                }
            )

        if status_value == FeedbackRequest.StatusChoices.SPAM and attrs.get("is_spam_suspected") is False:
            raise serializers.ValidationError(
                {
                    "is_spam_suspected": (
                        "Обращение со статусом 'Спам' не может иметь отрицательный флаг спама."
                    )
                }
            )

        return attrs
