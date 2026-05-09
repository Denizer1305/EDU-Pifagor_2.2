from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class AssignmentPolicy(TimeStampedModel):
    class CheckModeChoices(models.TextChoices):
        MANUAL = "manual", "Ручная проверка"
        AUTO = "auto", "Автопроверка"
        MIXED = "mixed", "Смешанная проверка"

    class GradingModeChoices(models.TextChoices):
        PASS_FAIL = "pass_fail", "Зачёт / незачёт"
        FIVE_POINT = "five_point", "Пятибалльная"
        HUNDRED_POINT = "hundred_point", "Стобалльная"
        PERCENTAGE = "percentage", "Проценты"
        RAW_SCORE = "raw_score", "Сырые баллы"
        RUBRIC = "rubric", "По критериям"

    assignment = models.OneToOneField(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="policy",
        verbose_name="Работа",
    )
    check_mode = models.CharField(
        max_length=32,
        choices=CheckModeChoices.choices,
        default=CheckModeChoices.MANUAL,
        verbose_name="Режим проверки",
    )
    grading_mode = models.CharField(
        max_length=32,
        choices=GradingModeChoices.choices,
        default=GradingModeChoices.RAW_SCORE,
        verbose_name="Режим оценивания",
    )
    max_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Максимальный балл",
    )
    passing_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Проходной балл",
    )
    attempts_limit = models.PositiveIntegerField(
        default=1,
        verbose_name="Лимит попыток",
    )
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Лимит времени, мин",
    )
    recommended_time_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Рекомендуемое время, мин",
    )
    shuffle_questions = models.BooleanField(
        default=False,
        verbose_name="Перемешивать вопросы",
    )
    shuffle_answers = models.BooleanField(
        default=False,
        verbose_name="Перемешивать ответы",
    )
    show_results_immediately = models.BooleanField(
        default=False,
        verbose_name="Показывать результат сразу",
    )
    show_correct_answers_after_submit = models.BooleanField(
        default=False,
        verbose_name="Показывать правильные ответы после отправки",
    )
    allow_late_submission = models.BooleanField(
        default=False,
        verbose_name="Разрешить просроченную сдачу",
    )
    late_penalty_percent = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Штраф за просрочку, %",
    )
    auto_submit_on_timeout = models.BooleanField(
        default=True,
        verbose_name="Автоотправка по таймеру",
    )
    requires_manual_review = models.BooleanField(
        default=False,
        verbose_name="Требуется ручная проверка",
    )
    allow_file_upload = models.BooleanField(
        default=False,
        verbose_name="Разрешить загрузку файлов",
    )
    allow_text_answer = models.BooleanField(
        default=True,
        verbose_name="Разрешить текстовый ответ",
    )
    allow_photo_upload = models.BooleanField(
        default=False,
        verbose_name="Разрешить фото",
    )

    class Meta:
        db_table = "assignments_assignment_policy"
        verbose_name = "Правило выполнения работы"
        verbose_name_plural = "Правила выполнения работ"

    def clean(self):
        errors: dict[str, str] = {}

        if self.max_score < 0:
            errors["max_score"] = "Максимальный балл не может быть отрицательным."

        if self.passing_score < 0:
            errors["passing_score"] = "Проходной балл не может быть отрицательным."

        if self.passing_score > self.max_score:
            errors["passing_score"] = (
                "Проходной балл не может быть больше максимального."
            )

        if self.late_penalty_percent > 100:
            errors["late_penalty_percent"] = "Штраф не может быть больше 100%."

        if (
            self.check_mode == self.CheckModeChoices.AUTO
            and self.requires_manual_review
        ):
            errors["requires_manual_review"] = (
                "Для автопроверки ручная проверка должна быть отключена."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"Правила: {self.assignment}"
