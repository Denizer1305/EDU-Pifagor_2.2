from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.journal.models.choices import TopicProgressStatus


class TopicProgress(models.Model):
    """Фактическое прохождение темы курса группой."""

    class TopicStatus(models.TextChoices):
        PLANNED = "planned", _("Запланирована")
        IN_PROGRESS = "in_progress", _("В процессе")
        COMPLETED = "completed", _("Пройдена")
        SKIPPED = "skipped", _("Пропущена")
        BEHIND = "behind", _("Отставание")

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="journal_topic_progress",
        verbose_name=_("Курс"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="journal_topic_progress",
        verbose_name=_("Группа"),
    )
    lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.CASCADE,
        related_name="journal_topic_progress",
        verbose_name=_("Плановая тема"),
    )
    journal_lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="topic_progress_records",
        verbose_name=_("Фактическое занятие"),
    )

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
    status = models.CharField(
        max_length=20,
        choices=TopicStatus.choices,
        default=TopicStatus.PLANNED,
        db_index=True,
        verbose_name=_("Статус прохождения"),
    )
    days_behind = models.SmallIntegerField(
        default=0,
        verbose_name=_("Дней отставания"),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий"),
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
        db_table = "journal_topic_progress"
        verbose_name = _("Прогресс по теме")
        verbose_name_plural = _("Прогресс по темам")
        ordering = ["course", "group", "lesson__order", "id"]
        indexes = [
            models.Index(
                fields=["course", "group"],
                name="idx_tprogress_course_group",
            ),
            models.Index(
                fields=["status"],
                name="idx_tprogress_status",
            ),
            models.Index(
                fields=["group", "status"],
                name="idx_tprogress_group_status",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "group", "lesson"],
                name="uniq_topic_progress_course_group_lesson",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.course} — {self.group} — {self.lesson}"

    @property
    def is_behind(self) -> bool:
        """Показывает, что тема отстаёт от плана."""

        return self.status == TopicProgressStatus.BEHIND

    def clean(self) -> None:
        errors: dict[str, str] = {}

        if (
            self.lesson_id
            and self.course_id
            and self.lesson.course_id != self.course_id
        ):
            errors["lesson"] = _("Плановая тема должна относиться к выбранному курсу.")

        if self.journal_lesson_id:
            if self.course_id and self.journal_lesson.course_id != self.course_id:
                errors["journal_lesson"] = _(
                    "Фактическое занятие должно относиться к выбранному курсу."
                )

            if self.group_id and self.journal_lesson.group_id != self.group_id:
                errors["journal_lesson"] = _(
                    "Фактическое занятие должно относиться к выбранной группе."
                )

        if self.actual_date and self.planned_date:
            self.days_behind = (self.actual_date - self.planned_date).days

        if errors:
            raise ValidationError(errors)
