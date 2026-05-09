from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class JournalSummary(models.Model):
    """Кэш сводной аналитики журнала.

    Не является источником истины.
    Пересчитывается через Celery после изменений в журнале.
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
        verbose_name=_("Группа"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="journal_summaries",
        verbose_name=_("Студент"),
    )

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
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name=_("Процент посещаемости"),
    )

    avg_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("1.00")),
            MaxValueValidator(Decimal("5.00")),
        ],
        verbose_name=_("Средний балл"),
    )
    debt_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Количество задолженностей"),
    )

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
        verbose_name=_("Тем с отставанием"),
    )
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name=_("Процент прохождения программы"),
    )

    calculated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Дата пересчёта"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления"),
    )

    class Meta:
        db_table = "journal_summary"
        verbose_name = _("Сводка журнала")
        verbose_name_plural = _("Сводки журнала")
        ordering = ["course", "group", "student_id"]
        indexes = [
            models.Index(
                fields=["course", "group"],
                name="idx_jsummary_course_group",
            ),
            models.Index(
                fields=["student"],
                name="idx_jsummary_student",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "group", "student"],
                condition=models.Q(student__isnull=False),
                name="uniq_jsummary_course_group_student",
            ),
            models.UniqueConstraint(
                fields=["course", "group"],
                condition=models.Q(student__isnull=True),
                name="uniq_jsummary_course_group_no_student",
            ),
        ]

    def __str__(self) -> str:
        if self.student_id:
            return f"{self.course} — {self.group} — {self.student}"

        return f"{self.course} — {self.group} — общая сводка"
