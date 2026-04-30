from __future__ import annotations

from django.db import models

from apps.assignments.models.base import TimeStampedModel


class PlagiarismCheck(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Ожидает"
        IN_PROGRESS = "in_progress", "В процессе"
        COMPLETED = "completed", "Завершено"
        ERROR = "error", "Ошибка"

    submission = models.OneToOneField(
        "assignments.Submission",
        on_delete=models.CASCADE,
        related_name="plagiarism_check",
        verbose_name="Сдача",
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name="Статус",
    )
    similarity_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Процент совпадения",
    )
    report_url = models.URLField(
        blank=True,
        verbose_name="Ссылка на отчёт",
    )
    raw_result_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Сырые данные JSON",
    )
    checked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Проверено",
    )

    class Meta:
        db_table = "assignments_plagiarism_check"
        verbose_name = "Проверка на заимствование"
        verbose_name_plural = "Проверки на заимствование"

    def __str__(self) -> str:
        return f"Антиплагиат: {self.submission}"
