from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import FeedbackRequest
from apps.feedback.serializers.feedback_attachment import FeedbackAttachmentSerializer


class FeedbackRequestBaseSerializer(serializers.ModelSerializer):
    attachments_count = serializers.IntegerField(read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_display = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = FeedbackRequest
        fields = (
            "id",
            "user",
            "type",
            "type_display",
            "status",
            "status_display",
            "source",
            "source_display",
            "subject",
            "message",
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
            "is_processed",
            "processed_at",
            "processed_by",
            "reply_message",
            "internal_note",
            "is_spam_suspected",
            "ip_address",
            "user_agent",
            "referrer",
            "attachments_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "type_display",
            "status_display",
            "source_display",
            "personal_data_consent_at",
            "is_processed",
            "processed_at",
            "processed_by",
            "is_spam_suspected",
            "ip_address",
            "user_agent",
            "referrer",
            "attachments_count",
            "created_at",
            "updated_at",
        )


class FeedbackRequestListSerializer(FeedbackRequestBaseSerializer):
    sender_display = serializers.SerializerMethodField(read_only=True)

    class Meta(FeedbackRequestBaseSerializer.Meta):
        fields = (
            "id",
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

    def get_sender_display(self, obj: FeedbackRequest) -> str:
        if obj.full_name:
            return obj.full_name
        if obj.user_id:
            return getattr(obj.user, "email", "—")
        return obj.email or "—"


class FeedbackRequestDetailSerializer(FeedbackRequestBaseSerializer):
    attachments = FeedbackAttachmentSerializer(many=True, read_only=True)
    sender_display = serializers.SerializerMethodField(read_only=True)
    processed_by_email = serializers.SerializerMethodField(read_only=True)

    class Meta(FeedbackRequestBaseSerializer.Meta):
        fields = FeedbackRequestBaseSerializer.Meta.fields + (
            "attachments",
            "sender_display",
            "processed_by_email",
        )
        read_only_fields = FeedbackRequestBaseSerializer.Meta.read_only_fields + (
            "attachments",
            "sender_display",
            "processed_by_email",
        )

    def get_sender_display(self, obj: FeedbackRequest) -> str:
        if obj.full_name:
            return obj.full_name
        if obj.user_id:
            return getattr(obj.user, "email", "—")
        return obj.email or "—"

    def get_processed_by_email(self, obj: FeedbackRequest) -> str:
        if obj.processed_by_id:
            return obj.processed_by.email
        return ""


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
        if len(attachments) > 5:
            raise serializers.ValidationError(
                {
                    "attachments": "Можно прикрепить не более 5 файлов."
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
        if len(attachments) > 5:
            raise serializers.ValidationError(
                {
                    "attachments": "Можно прикрепить не более 5 файлов."
                }
            )

        if not attrs.get("subject") and attrs.get("error_title"):
            attrs["subject"] = attrs["error_title"]

        return attrs


class FeedbackRequestAdminUpdateSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = FeedbackRequest
        fields = (
            "status",
            "reply_message",
            "internal_note",
            "is_spam_suspected",
            "is_processed",
        )

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

        return attrs
