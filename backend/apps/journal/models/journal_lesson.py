from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class LessonStatus(models.TextChoices):
    """Статус занятия в журнале."""

    PLANNED = "planned", _("Запланировано")
    CONDUCTED = "conducted", _("Проведено")
    CANCELLED = "cancelled", _("Отменено")
    POSTPONED = "postponed", _("Перенесено")
    REPLACED = "replaced", _("Замена")


class JournalLesson(models.Model):
    """
    Занятие в электронном журнале.

    Представляет конкретный факт проведения (или планирования) урока
    в рамках курса для учебной группы. Может быть связано с уроком
    из модуля course/ (если курс построен по КТП), либо быть
    самостоятельным записью без привязки к структуре курса.
    """

    # --- Связи с другими модулями ---
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
        verbose_name=_("Учебная группа"),
    )
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="journal_lessons",
        verbose_name=_("Преподаватель"),
    )
    # Опциональная привязка к уроку из структуры курса (КТП)
    course_lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_lessons",
        verbose_name=_("Урок курса (КТП)"),
    )

    # --- Дата и время ---
    date = models.DateField(
        verbose_name=_("Дата занятия"),
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

    # --- Тема ---
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

    # --- Домашнее задание ---
    homework = models.TextField(
        blank=True,
        verbose_name=_("Домашнее задание"),
    )

    # --- Статус и комментарий ---
    status = models.CharField(
        max_length=20,
        choices=LessonStatus.choices,
        default=LessonStatus.PLANNED,
        verbose_name=_("Статус"),
        db_index=True,
    )
    teacher_comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий преподавателя"),
    )

    # --- Порядковый номер занятия в рамках курса/группы ---
    lesson_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Номер занятия"),
    )

    # --- Служебные поля ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = _("Занятие журнала")
        verbose_name_plural = _("Занятия журнала")
        db_table = "journal_lesson"
        ordering = ["date", "started_at"]
        indexes = [
            models.Index(
                fields=["course", "group", "date"], name="idx_jlesson_course_group_date"
            ),
            models.Index(fields=["teacher", "date"], name="idx_jlesson_teacher_date"),
            models.Index(fields=["status"], name="idx_jlesson_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "group", "date", "lesson_number"],
                name="uniq_jlesson_course_group_date_num",
                condition=models.Q(lesson_number__isnull=False),
            )
        ]

    def __str__(self) -> str:
        topic = self.actual_topic or self.planned_topic or "—"
        return f"{self.date} | {self.group} | {topic[:60]}"

    @property
    def topic(self) -> str:
        """Возвращает фактическую тему, если проведено, иначе плановую."""
        return self.actual_topic or self.planned_topic
