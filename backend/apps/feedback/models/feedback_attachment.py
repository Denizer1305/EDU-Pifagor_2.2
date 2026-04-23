from __future__ import annotations

import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.feedback.models.base import TimeStampedModel, normalize_text
from apps.feedback.models.feedback_request import FeedbackRequest


def feedback_attachment_upload_to(instance, filename):
    """
    Оставляем это имя для совместимости со старыми миграциями.
    """
    ext = os.path.splitext(filename)[1].lower()
    return f"feedback/attachments/{uuid.uuid4().hex}{ext}"


class FeedbackAttachment(TimeStampedModel):
    class FileKindChoices(models.TextChoices):
        IMAGE = "image", "Изображение"
        PDF = "pdf", "PDF"
        DOCUMENT = "document", "Документ"
        OTHER = "other", "Другое"

    ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".pdf",
        ".doc",
        ".docx",
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024

    class Meta:
        db_table = "feedback_attachment"
        verbose_name = "Вложение обращения"
        verbose_name_plural = "Вложения обращений"
        indexes = [
            models.Index(fields=("feedback_request", "created_at")),
            models.Index(fields=("kind",)),
        ]

    feedback_request = models.ForeignKey(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Обращение",
    )
    file = models.FileField(
        upload_to=feedback_attachment_upload_to,
        verbose_name="Файл",
    )
    original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Оригинальное имя файла",
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="MIME-тип",
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name="Размер файла",
    )
    kind = models.CharField(
        max_length=32,
        choices=FileKindChoices.choices,
        default=FileKindChoices.OTHER,
        verbose_name="Тип файла",
    )

    def clean(self):
        errors: dict[str, str] = {}

        if not self.file:
            errors["file"] = "Файл обязателен."

        filename = getattr(self.file, "name", "") or self.original_name
        ext = os.path.splitext(filename)[1].lower()

        if ext and ext not in self.ALLOWED_EXTENSIONS:
            errors["file"] = "Поддерживаются только изображения, PDF, DOC и DOCX."

        file_size = getattr(self.file, "size", 0) or self.file_size
        if file_size > self.MAX_FILE_SIZE:
            errors["file"] = "Размер файла не должен превышать 10 МБ."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.file:
            self.original_name = (
                normalize_text(self.original_name) or os.path.basename(self.file.name)
            )
            self.file_size = getattr(self.file, "size", 0) or 0
            self.mime_type = getattr(self.file, "content_type", "") or ""

            ext = os.path.splitext(self.original_name)[1].lower()
            if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                self.kind = self.FileKindChoices.IMAGE
            elif ext == ".pdf":
                self.kind = self.FileKindChoices.PDF
            elif ext in {".doc", ".docx"}:
                self.kind = self.FileKindChoices.DOCUMENT
            else:
                self.kind = self.FileKindChoices.OTHER

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_name or f"Вложение #{self.pk}"
