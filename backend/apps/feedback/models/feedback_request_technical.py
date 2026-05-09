from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.feedback.models.base import TimeStampedModel, normalize_text
from apps.feedback.models.feedback_request import FeedbackRequest


class FeedbackRequestTechnical(TimeStampedModel):
    class Meta:
        db_table = "feedback_request_technical"
        verbose_name = "Технический контекст обращения"
        verbose_name_plural = "Технические контексты обращений"
        indexes = [
            models.Index(fields=("error_code",)),
            models.Index(fields=("client_platform",)),
        ]

    feedback_request = models.OneToOneField(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="technical",
        verbose_name="Обращение",
    )
    page_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL страницы",
    )
    frontend_route = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Frontend route",
    )
    error_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Код ошибки",
    )
    error_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Заголовок ошибки",
    )
    error_details = models.TextField(
        blank=True,
        verbose_name="Детали ошибки",
    )
    client_platform = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Клиентская платформа",
    )
    app_version = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Версия приложения",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP-адрес",
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User agent",
    )
    referrer = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="Referrer",
    )
    extra_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Дополнительные технические данные",
    )

    def clean(self):
        if (
            self.feedback_request.source == FeedbackRequest.SourceChoices.ERROR_MODAL
            and not any(
                [
                    normalize_text(self.page_url),
                    normalize_text(self.frontend_route),
                    normalize_text(self.error_code),
                    normalize_text(self.error_title),
                    normalize_text(self.error_details),
                ]
            )
        ):
            raise ValidationError(
                {
                    "error_details": (
                        "Для обращения из окна ошибки нужно передать хотя бы часть "
                        "технического контекста."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.page_url = normalize_text(self.page_url)
        self.frontend_route = normalize_text(self.frontend_route)
        self.error_code = normalize_text(self.error_code)
        self.error_title = normalize_text(self.error_title)
        self.error_details = normalize_text(self.error_details)
        self.client_platform = normalize_text(self.client_platform)
        self.app_version = normalize_text(self.app_version)
        self.user_agent = normalize_text(self.user_agent)
        self.referrer = normalize_text(self.referrer)

        if self.extra_payload is None:
            self.extra_payload = {}

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.error_title or self.error_code or "Технический контекст"
