from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import FeedbackRequest
from apps.feedback.services.feedback_services import MAX_ATTACHMENTS_PER_REQUEST


def _validate_attachments_count(attachments: list) -> None:
    """Проверяет лимит вложений для обращения."""

    if len(attachments) > MAX_ATTACHMENTS_PER_REQUEST:
        raise serializers.ValidationError(
            {
                "attachments": (
                    f"Можно прикрепить не более "
                    f"{MAX_ATTACHMENTS_PER_REQUEST} файлов."
                )
            }
        )


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

        _validate_attachments_count(attrs.get("attachments") or [])

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

        _validate_attachments_count(attrs.get("attachments") or [])

        if not attrs.get("subject") and attrs.get("error_title"):
            attrs["subject"] = attrs["error_title"]

        return attrs
