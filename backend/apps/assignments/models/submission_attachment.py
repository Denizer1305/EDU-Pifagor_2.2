from __future__ import annotations

import os

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


def submission_attachment_upload_to(instance, filename: str) -> str:
    submission_id = instance.submission_id or "unknown"
    return os.path.join("assignments", "submission_attachments", str(submission_id), filename)


class SubmissionAttachment(TimeStampedModel):
    class AttachmentTypeChoices(models.TextChoices):
        DOCUMENT = "document", "Документ"
        IMAGE = "image", "Изображение"
        ARCHIVE = "archive", "Архив"
        PRESENTATION = "presentation", "Презентация"
        SPREADSHEET = "spreadsheet", "Таблица"
        OTHER = "other", "Другое"

    submission = models.ForeignKey(
        "assignments.Submission",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Сдача",
    )
    question = models.ForeignKey(
        "assignments.AssignmentQuestion",
        on_delete=models.CASCADE,
        related_name="submission_attachments",
        null=True,
        blank=True,
        verbose_name="Вопрос",
    )
    file = models.FileField(
        upload_to=submission_attachment_upload_to,
        verbose_name="Файл",
    )
    original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Оригинальное имя",
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
    attachment_type = models.CharField(
        max_length=32,
        choices=AttachmentTypeChoices.choices,
        default=AttachmentTypeChoices.OTHER,
        verbose_name="Тип вложения",
    )

    class Meta:
        db_table = "assignments_submission_attachment"
        verbose_name = "Вложение ответа"
        verbose_name_plural = "Вложения ответов"
        indexes = [
            models.Index(fields=("submission",)),
            models.Index(fields=("question",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        if not self.file:
            errors["file"] = "Файл обязателен."

        if self.question_id and self.question.assignment_id != self.submission.assignment_id:
            errors["question"] = "Вопрос должен относиться к работе в выбранной сдаче."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.file:
            self.original_name = os.path.basename(self.file.name)
            self.file_size = getattr(self.file, "size", 0) or 0
            self.mime_type = getattr(self.file, "content_type", "") or ""

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_name or f"Вложение #{self.pk}"
