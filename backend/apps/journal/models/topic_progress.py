from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class TopicProgressStatus(models.TextChoices):
    """Статус прохождения темы/элемента КТП."""

    PLANNED = "planned", _("По плану")
    COMPLETED = "completed", _("Пройдено")
    POSTPONED = "postponed", _("Перенесено")
    SKIPPED = "skipped", _("Пропущено")
    BEHIND = "behind", _("Отставание")


class TopicProgress(models.Model):
    """
    Прогресс прохождения темы или элемента КТП в рамках курса для группы.

    Связывает плановый урок из course/ с реальным фактом прохождения.
    Позволяет отслеживать, идёт ли группа по плану или отстаёт.
    """

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="topic_progress_records",
        verbose_name=_("Курс"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="topic_progress_records",
        verbose_name=_("Учебная группа"),
    )
    # Урок из КТП курса
    lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.CASCADE,
        related_name="topic_progress_records",
        verbose_name=_("Урок курса (КТП)"),
    )
    # Фактическое занятие, на котором тема была пройдена
    journal_lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="topic_progress_records",
        verbose_name=_("Занятие журнала"),
    )

    # --- Даты ---
    planned_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Плановая дата"),
    )
    actual_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Фактическая дата"),
    )

    # --- Статус ---
    status = models.CharField(
        max_length=20,
        choices=TopicProgressStatus.choices,
        default=TopicProgressStatus.PLANNED,
        verbose_name=_("Статус"),
        db_index=True,
    )

    # --- Отставание ---
    days_behind = models.SmallIntegerField(
        default=0,
        verbose_name=_("Отставание (дней)"),
        help_text=_("Положительное — отставание, отрицательное — опережение"),
    )

    comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий"),
    )

    # --- Служебные поля ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = _("Прогресс темы")
        verbose_name_plural = _("Прогресс тем")
        db_table = "journal_topic_progress"
        ordering = ["planned_date", "lesson"]
        indexes = [
            models.Index(fields=["course", "group"], name="idx_tprogress_course_group"),
            models.Index(fields=["status"], name="idx_tprogress_status"),
            models.Index(fields=["group", "status"], name="idx_tprogress_group_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "group", "lesson"],
                name="uniq_topic_progress_course_group_lesson",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.group} | {self.lesson} | "
            f"{self.get_status_display()} | план: {self.planned_date}"
        )

    @property
    def is_behind(self) -> bool:
        return self.days_behind > 0
