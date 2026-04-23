from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.feedback.models.base import TimeStampedModel, normalize_text
from apps.feedback.models.feedback_request import FeedbackRequest


class FeedbackRequestContact(TimeStampedModel):
    class Meta:
        db_table = "feedback_request_contact"
        verbose_name = "Контактные данные обращения"
        verbose_name_plural = "Контактные данные обращений"

    feedback_request = models.OneToOneField(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="contact",
        verbose_name="Обращение",
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ФИО",
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        verbose_name="Email",
    )
    phone = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Телефон",
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Организация",
    )

    def clean(self):
        errors: dict[str, str] = {}

        if (
            self.feedback_request.source == FeedbackRequest.SourceChoices.CONTACTS_PAGE
            and not normalize_text(self.email)
        ):
            errors["email"] = "Для формы контактов необходимо указать email."

        if not self.feedback_request.user and not normalize_text(self.email):
            errors["email"] = (
                "Для неавторизованного обращения необходимо указать email."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_name = normalize_text(self.full_name)
        self.email = normalize_text(self.email)
        self.phone = normalize_text(self.phone)
        self.organization_name = normalize_text(self.organization_name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.full_name or self.email or "Контакт обращения"
