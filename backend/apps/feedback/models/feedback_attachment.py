from __future__ import annotations

import os

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def feedback_attachment_upload_to(instance, filename: str) -> str:
    feedback_request_id = instance.feedback_request_id or "unassigned"
    return f"feedback/{feedback_request_id}/{filename}"


class FeedbackAttachment(models.Model):
    class FileTypeChoices(models.TextChoices):
        IMAGE = "image", _("Изображение")
        PDF = "pdf", _("PDF")
        DOC = "doc", _("DOC / DOCX")
        OTHER = "other", _("Другое")

    feedback_request = models.ForeignKey(
        "feedback.FeedbackRequest",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Обращение"),
    )
    file = models.FileField(
        _("Файл"),
        upload_to=feedback_attachment_upload_to,
    )
    original_name = models.CharField(
        _("Оригинальное имя файла"),
        max_length=255,
        blank=True,
    )
    file_type = models.CharField(
        _("Тип файла"),
        max_length=16,
        choices=FileTypeChoices.choices,
        default=FileTypeChoices.OTHER,
    )
    file_size = models.PositiveIntegerField(
        _("Размер файла в байтах"),
        default=0,
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )

    class Meta:
        db_table = "feedback_attachment"
        verbose_name = _("Вложение обращения")
        verbose_name_plural = _("Вложения обращений")
        ordering = ("created_at",)

    def __str__(self) -> str:
        return self.original_name or os.path.basename(self.file.name)

    def clean(self) -> None:
        super().clean()

        errors: dict[str, str] = {}

        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            allowed_ext = {
                ".jpg", ".jpeg", ".png", ".gif", ".webp",
                ".pdf", ".doc", ".docx",
            }

            if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                self.file_type = self.FileTypeChoices.IMAGE
            elif ext == ".pdf":
                self.file_type = self.FileTypeChoices.PDF
            elif ext in {".doc", ".docx"}:
                self.file_type = self.FileTypeChoices.DOC
            else:
                self.file_type = self.FileTypeChoices.OTHER

            if ext not in allowed_ext:
                errors["file"] = _(
                    "Поддерживаются только изображения, PDF, DOC и DOCX."
                )

            file_size = getattr(self.file, "size", 0) or 0
            self.file_size = file_size

            max_size = 10 * 1024 * 1024
            if file_size > max_size:
                errors["file"] = _(
                    "Размер файла не должен превышать 10 МБ."
                )

            if not self.original_name:
                self.original_name = os.path.basename(self.file.name)

        if errors:
            raise ValidationError(errors)
