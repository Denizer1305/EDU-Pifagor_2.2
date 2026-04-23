from __future__ import annotations

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.feedback.models.base import TimeStampedModel, normalize_text


class FeedbackRequest(TimeStampedModel):
    class TypeChoices(models.TextChoices):
        QUESTION = "question", "Вопрос"
        BUG = "bug", "Ошибка"
        IDEA = "idea", "Идея"
        COMPLAINT = "complaint", "Жалоба"
        ACCESS = "access", "Доступ"
        TECHNICAL = "technical", "Техническое обращение"
        OTHER = "other", "Другое"

    class StatusChoices(models.TextChoices):
        NEW = "new", "Новое"
        IN_PROGRESS = "in_progress", "В работе"
        WAITING_USER = "waiting_user", "Ожидает пользователя"
        RESOLVED = "resolved", "Решено"
        REJECTED = "rejected", "Отклонено"
        SPAM = "spam", "Спам"
        ARCHIVED = "archived", "В архиве"

    class SourceChoices(models.TextChoices):
        CONTACTS_PAGE = "contacts_page", "Страница контактов"
        ERROR_MODAL = "error_modal", "Модальное окно ошибки"
        COURSE_PAGE = "course_page", "Страница курса"
        PROFILE_PAGE = "profile_page", "Страница профиля"
        OTHER = "other", "Другое"

    class Meta:
        db_table = "feedback_request"
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "created_at")),
            models.Index(fields=("type", "created_at")),
            models.Index(fields=("source", "created_at")),
            models.Index(fields=("user", "created_at")),
            models.Index(fields=("status", "type")),
        ]

    uid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="UID",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="feedback_requests",
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    type = models.CharField(
        max_length=32,
        choices=TypeChoices.choices,
        default=TypeChoices.QUESTION,
        verbose_name="Тип обращения",
        db_index=True,
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        verbose_name="Статус",
        db_index=True,
    )
    source = models.CharField(
        max_length=32,
        choices=SourceChoices.choices,
        default=SourceChoices.CONTACTS_PAGE,
        verbose_name="Источник",
        db_index=True,
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Тема",
    )
    message = models.TextField(
        verbose_name="Сообщение",
    )
    is_personal_data_consent = models.BooleanField(
        default=False,
        verbose_name="Согласие на обработку персональных данных",
    )
    personal_data_consent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата согласия на обработку персональных данных",
    )

    def clean(self):
        errors: dict[str, list[str] | str] = {}

        if not normalize_text(self.message):
            errors["message"] = "Сообщение не может быть пустым."

        if len(normalize_text(self.message)) < 5:
            errors["message"] = "Сообщение должно содержать не менее 5 символов."

        if not self.is_personal_data_consent:
            errors["is_personal_data_consent"] = (
                "Нужно подтвердить согласие на обработку персональных данных."
            )

        if self.personal_data_consent_at and not self.is_personal_data_consent:
            errors["personal_data_consent_at"] = (
                "Дата согласия не может быть заполнена без самого согласия."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.subject = normalize_text(self.subject)
        self.message = normalize_text(self.message)

        if self.is_personal_data_consent and self.personal_data_consent_at is None:
            self.personal_data_consent_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_processed(self) -> bool:
        processing = getattr(self, "processing", None)
        return bool(processing and processing.processed_at)

    def __str__(self) -> str:
        display_subject = self.subject or "Без темы"
        return f"{display_subject} [{self.get_status_display()}]"
