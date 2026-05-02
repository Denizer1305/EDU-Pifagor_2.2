from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class JournalLesson(models.Model):
    """Фактически проведённое занятие в электронном журнале."""

    class LessonStatus(models.TextChoices):
        PLANNED = "planned", _("Запланировано")
        COMPLETED = "completed", _("Проведено")
        CANCELLED = "cancelled", _("Отменено")
        RESCHEDULED = "rescheduled", _("Перенесено")

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="journal_lessons",
        verbose_name=_("Курс"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="journal_lessons",
        verbose_name=_("Группа"),
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_lessons_as_teacher",
        verbose_name=_("Преподаватель"),
    )
    course_lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_lessons",
        verbose_name=_("Плановая тема курса"),
    )

    date = models.DateField(verbose_name=_("Дата занятия"))
    lesson_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Номер занятия в дне"),
    )
    started_at = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Время начала"),
    )
    ended_at = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_("Время окончания"),
    )

    planned_topic = models.CharField(
        max_length=512,
        blank=True,
        verbose_name=_("Плановая тема"),
    )
    actual_topic = models.CharField(
        max_length=512,
        blank=True,
        verbose_name=_("Фактическая тема"),
    )
    homework = models.TextField(
        blank=True,
        verbose_name=_("Домашнее задание"),
    )
    status = models.CharField(
        max_length=20,
        choices=LessonStatus.choices,
        default=LessonStatus.PLANNED,
        db_index=True,
        verbose_name=_("Статус"),
    )
    teacher_comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий преподавателя"),
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
        db_table = "journal_lesson"
        verbose_name = _("Занятие журнала")
        verbose_name_plural = _("Занятия журнала")
        ordering = ["-date", "lesson_number", "id"]
        indexes = [
            models.Index(
                fields=["course", "group", "date"],
                name="idx_jlesson_course_group_date",
            ),
            models.Index(
                fields=["teacher", "date"],
                name="idx_jlesson_teacher_date",
            ),
            models.Index(
                fields=["status"],
                name="idx_jlesson_status",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "group", "date", "lesson_number"],
                condition=models.Q(lesson_number__isnull=False),
                name="uniq_jlesson_course_group_date_num",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.course} — {self.group} — {self.date}"

    def clean(self) -> None:
        errors: dict[str, str] = {}

        if self.started_at and self.ended_at and self.ended_at <= self.started_at:
            errors["ended_at"] = _("Время окончания должно быть позже времени начала.")

        if self.course_lesson_id and self.course_id:
            if self.course_lesson.course_id != self.course_id:
                errors["course_lesson"] = _(
                    "Плановая тема должна относиться к выбранному курсу."
                )

        if self.course_id and self.group_id:
            group_subject = getattr(self.course, "group_subject", None)

            if group_subject is not None and group_subject.group_id != self.group_id:
                errors["group"] = _(
                    "Группа занятия должна совпадать с группой учебного курса."
                )

        if errors:
            raise ValidationError(errors)
