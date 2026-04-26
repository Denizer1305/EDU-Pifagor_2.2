from __future__ import annotations

import os

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel, normalize_text


def assignment_attachment_upload_to(instance, filename: str) -> str:
    assignment_uid = instance.assignment.uid if instance.assignment_id else "unknown"
    return os.path.join("assignments", "attachments", str(assignment_uid), filename)


class AssignmentAttachment(TimeStampedModel):
    class AttachmentTypeChoices(models.TextChoices):
        STATEMENT = "statement", "Условие"
        ANSWER_KEY = "answer_key", "Ответы"
        CRITERIA = "criteria", "Критерии"
        BLANK = "blank", "Бланк"
        PRESENTATION = "presentation", "Презентация"
        REFERENCE = "reference", "Справочный материал"
        OFFICIAL_PDF = "official_pdf", "Официальный PDF"
        SAMPLE_SOLUTION = "sample_solution", "Образец решения"

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Работа",
    )
    variant = models.ForeignKey(
        "assignments.AssignmentVariant",
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name="Вариант",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название вложения",
    )
    attachment_type = models.CharField(
        max_length=32,
        choices=AttachmentTypeChoices.choices,
        default=AttachmentTypeChoices.REFERENCE,
        verbose_name="Тип вложения",
    )
    file = models.FileField(
        upload_to=assignment_attachment_upload_to,
        null=True,
        blank=True,
        verbose_name="Файл",
    )
    external_url = models.URLField(
        blank=True,
        verbose_name="Внешняя ссылка",
    )
    is_visible_to_students = models.BooleanField(
        default=True,
        verbose_name="Видно студентам",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядок",
    )

    class Meta:
        db_table = "assignments_assignment_attachment"
        verbose_name = "Вложение работы"
        verbose_name_plural = "Вложения работ"
        ordering = ("order", "id")
        indexes = [
            models.Index(fields=("assignment", "variant")),
            models.Index(fields=("attachment_type",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        self.title = normalize_text(self.title)
        if not self.title:
            errors["title"] = "Название вложения обязательно."

        if self.variant_id and self.variant.assignment_id != self.assignment_id:
            errors["variant"] = "Вариант должен принадлежать выбранной работе."

        if not self.file and not self.external_url:
            errors["file"] = "Нужно прикрепить файл или указать ссылку."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.title
