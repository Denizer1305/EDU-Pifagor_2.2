from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import (
    LessonType,
    ScheduleSourceType,
    ScheduleStatus,
    Weekday,
)
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduledLesson(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="scheduled_lessons",
        verbose_name=_("Организация"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="scheduled_lessons",
        verbose_name=_("Учебный год"),
    )
    education_period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Учебный период"),
    )
    pattern = models.ForeignKey(
        "schedule.SchedulePattern",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Шаблон занятия"),
    )
    date = models.DateField(
        _("Дата"),
        db_index=True,
    )
    weekday = models.PositiveSmallIntegerField(
        _("День недели"),
        choices=Weekday.choices,
        db_index=True,
    )
    time_slot = models.ForeignKey(
        "schedule.ScheduleTimeSlot",
        on_delete=models.PROTECT,
        related_name="scheduled_lessons",
        verbose_name=_("Временной слот"),
    )
    starts_at = models.TimeField(
        _("Время начала"),
    )
    ends_at = models.TimeField(
        _("Время окончания"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Группа"),
    )
    subject = models.ForeignKey(
        "organizations.Subject",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Предмет"),
    )
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons_as_teacher",
        null=True,
        blank=True,
        verbose_name=_("Преподаватель"),
    )
    room = models.ForeignKey(
        "schedule.ScheduleRoom",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Аудитория"),
    )
    group_subject = models.ForeignKey(
        "education.GroupSubject",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Предмет группы"),
    )
    teacher_group_subject = models.ForeignKey(
        "education.TeacherGroupSubject",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Преподаватель предмета группы"),
    )
    course = models.ForeignKey(
        "course.Course",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Курс"),
    )
    course_lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Занятие курса"),
    )
    journal_lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Занятие журнала"),
    )
    title = models.CharField(
        _("Название"),
        max_length=255,
        blank=True,
    )
    planned_topic = models.TextField(
        _("Плановая тема"),
        blank=True,
    )
    lesson_type = models.CharField(
        _("Тип занятия"),
        max_length=32,
        choices=LessonType.choices,
        default=LessonType.LESSON,
        db_index=True,
    )
    source_type = models.CharField(
        _("Источник"),
        max_length=32,
        choices=ScheduleSourceType.choices,
        default=ScheduleSourceType.MANUAL,
        db_index=True,
    )
    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=ScheduleStatus.choices,
        default=ScheduleStatus.DRAFT,
        db_index=True,
    )
    generated_from_pattern = models.BooleanField(
        _("Сгенерировано из шаблона"),
        default=False,
        db_index=True,
    )
    generation_batch = models.ForeignKey(
        "schedule.ScheduleGenerationBatch",
        on_delete=models.SET_NULL,
        related_name="scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Пакет генерации"),
    )
    is_locked = models.BooleanField(
        _("Заблокировано от автогенерации"),
        default=False,
        db_index=True,
    )
    is_public = models.BooleanField(
        _("Опубликовано для пользователей"),
        default=False,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Кто создал"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_scheduled_lessons",
        null=True,
        blank=True,
        verbose_name=_("Кто обновил"),
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "scheduled_lessons"
        verbose_name = _("Занятие расписания")
        verbose_name_plural = _("Занятия расписания")
        ordering = ("date", "time_slot", "group", "subject")
        indexes = [
            models.Index(fields=("organization", "date")),
            models.Index(fields=("organization", "academic_year", "education_period")),
            models.Index(fields=("date", "time_slot")),
            models.Index(fields=("group", "date", "time_slot")),
            models.Index(fields=("teacher", "date", "time_slot")),
            models.Index(fields=("room", "date", "time_slot")),
            models.Index(fields=("course", "course_lesson")),
            models.Index(fields=("status", "is_public")),
            models.Index(fields=("generated_from_pattern", "is_locked")),
        ]

    def __str__(self) -> str:
        title = self.title or self.subject or self.course_lesson or _("Занятие")
        return f"{self.date} {self.time_slot}: {title}"

    def clean(self) -> None:
        super().clean()

        errors: dict[str, str] = {}

        if self.ends_at <= self.starts_at:
            errors["ends_at"] = _("Время окончания должно быть позже времени начала.")

        if (
            self.course_lesson_id
            and self.course_id
            and self.course_lesson.course_id != self.course_id
        ):
            errors["course_lesson"] = _(
                "Занятие курса должно относиться к выбранному курсу."
            )

        if (
            self.group_subject_id
            and self.group_id
            and self.group_subject.group_id != self.group_id
        ):
            errors["group_subject"] = _(
                "Предмет группы должен относиться к выбранной группе."
            )

            if self.subject_id and self.group_subject.subject_id != self.subject_id:
                errors["group_subject"] = _(
                    "Предмет группы должен соответствовать выбранному предмету."
                )

        if errors:
            raise ValidationError(errors)
