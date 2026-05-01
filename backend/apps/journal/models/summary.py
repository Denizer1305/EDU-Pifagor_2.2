from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class JournalSummary(models.Model):
    """
    Денормализованный агрегат-кэш по журналу.

    Пересчитывается через Celery-задачи или сигналы при изменении
    оценок, посещаемости, прогресса тем. Позволяет отдавать
    сводную статистику без тяжёлых агрегатных запросов в реальном времени.

    Гранулярность: курс + группа + (опционально) студент.
    Если student=None — это срез по всей группе.
    Если student задан — индивидуальный срез.
    """

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="journal_summaries",
        verbose_name=_("Курс"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="journal_summaries",
        verbose_name=_("Учебная группа"),
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="journal_summaries",
        verbose_name=_("Студент"),
        help_text=_("Если не задан — это агрегат по группе"),
    )

    # --- Посещаемость ---
    total_lessons = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Всего занятий"),
    )
    attended_lessons = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Посещено занятий"),
    )
    absent_lessons = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Пропущено занятий"),
    )
    attendance_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Посещаемость (%)"),
    )

    # --- Успеваемость ---
    avg_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Средний балл"),
    )
    debt_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Количество задолженностей"),
    )

    # --- Прогресс по КТП ---
    total_topics = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Всего тем"),
    )
    completed_topics = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Пройдено тем"),
    )
    topics_behind = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Тем в отставании"),
    )
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Прогресс по курсу (%)"),
    )

    # --- Служебные поля ---
    calculated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Последний пересчёт"),
    )

    class Meta:
        verbose_name = _("Сводка журнала")
        verbose_name_plural = _("Сводки журнала")
        db_table = "journal_summary"
        indexes = [
            models.Index(fields=["course", "group"], name="idx_jsummary_course_group"),
            models.Index(fields=["student"], name="idx_jsummary_student"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "group", "student"],
                name="uniq_jsummary_course_group_student",
                condition=models.Q(student__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["course", "group"],
                name="uniq_jsummary_course_group_no_student",
                condition=models.Q(student__isnull=True),
            ),
        ]

    def __str__(self) -> str:
        subject = str(self.student) if self.student_id else "группа"
        return str(f"{self.group} | {self.course} | {subject}")
