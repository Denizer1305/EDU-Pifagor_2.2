from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class AssignmentQuestion(TimeStampedModel):
    class QuestionTypeChoices(models.TextChoices):
        SINGLE_CHOICE = "single_choice", "Один вариант"
        MULTIPLE_CHOICE = "multiple_choice", "Несколько вариантов"
        SHORT_TEXT = "short_text", "Короткий ответ"
        LONG_TEXT = "long_text", "Развёрнутый ответ"
        NUMBER = "number", "Число"
        MATCHING = "matching", "Соответствие"
        ORDERING = "ordering", "Порядок"
        FILE_UPLOAD = "file_upload", "Загрузка файла"
        PHOTO_UPLOAD = "photo_upload", "Загрузка фото"
        LINK = "link", "Ссылка"
        TABLE = "table", "Таблица"
        CODE = "code", "Код"
        MANUAL_ONLY = "manual_only", "Только ручная проверка"

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Работа",
    )
    variant = models.ForeignKey(
        "assignments.AssignmentVariant",
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
        verbose_name="Вариант",
    )
    section = models.ForeignKey(
        "assignments.AssignmentSection",
        on_delete=models.CASCADE,
        related_name="questions",
        null=True,
        blank=True,
        verbose_name="Секция",
    )
    question_type = models.CharField(
        max_length=32,
        choices=QuestionTypeChoices.choices,
        default=QuestionTypeChoices.SHORT_TEXT,
        verbose_name="Тип вопроса",
    )
    prompt = models.TextField(
        verbose_name="Формулировка",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    answer_options_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Варианты ответов JSON",
    )
    correct_answer_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Правильный ответ JSON",
    )
    validation_rules_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Правила валидации JSON",
    )
    explanation = models.TextField(
        blank=True,
        verbose_name="Пояснение",
    )
    max_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Максимальный балл",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядок",
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Обязательный",
    )
    requires_manual_review = models.BooleanField(
        default=False,
        verbose_name="Требует ручной проверки",
    )

    class Meta:
        db_table = "assignments_assignment_question"
        verbose_name = "Вопрос работы"
        verbose_name_plural = "Вопросы работ"
        ordering = ("order", "id")
        indexes = [
            models.Index(fields=("assignment", "variant", "section")),
            models.Index(fields=("question_type",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        if not self.prompt:
            errors["prompt"] = "Формулировка вопроса обязательна."

        if self.variant_id and self.variant.assignment_id != self.assignment_id:
            errors["variant"] = "Вариант должен принадлежать выбранной работе."

        if self.section_id and self.section.assignment_id != self.assignment_id:
            errors["section"] = "Секция должна принадлежать выбранной работе."

        if (
            self.section_id
            and self.variant_id
            and self.section.variant_id
            and self.section.variant_id != self.variant_id
        ):
            errors["section"] = "Секция должна принадлежать выбранному варианту."

        if self.question_type == self.QuestionTypeChoices.MANUAL_ONLY:
            self.requires_manual_review = True

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"Вопрос #{self.pk or 'new'}"
