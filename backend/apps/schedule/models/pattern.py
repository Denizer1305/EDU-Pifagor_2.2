from __future__ import annotations

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


class SchedulePattern(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_patterns",
        verbose_name=_("Организация"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="schedule_patterns",
        verbose_name=_("Учебный год"),
    )
    education_period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Учебный период"),
    )
    week_template = models.ForeignKey(
        "schedule.ScheduleWeekTemplate",
        on_delete=models.SET_NULL,
        related_name="patterns",
        null=True,
        blank=True,
        verbose_name=_("Шаблон недели"),
    )
    weekday = models.PositiveSmallIntegerField(
        _("День недели"),
        choices=Weekday.choices,
        db_index=True,
    )
    time_slot = models.ForeignKey(
        "schedule.ScheduleTimeSlot",
        on_delete=models.PROTECT,
        related_name="patterns",
        verbose_name=_("Временной слот"),
    )
    starts_at = models.TimeField(
        _("Время начала"),
        null=True,
        blank=True,
    )
    ends_at = models.TimeField(
        _("Время окончания"),
        null=True,
        blank=True,
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Группа"),
    )
    subject = models.ForeignKey(
        "organizations.Subject",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Предмет"),
    )
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns_as_teacher",
        null=True,
        blank=True,
        verbose_name=_("Преподаватель"),
    )
    room = models.ForeignKey(
        "schedule.ScheduleRoom",
        on_delete=models.SET_NULL,
        related_name="patterns",
        null=True,
        blank=True,
        verbose_name=_("Аудитория"),
    )
    group_subject = models.ForeignKey(
        "education.GroupSubject",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Предмет группы"),
    )
    teacher_group_subject = models.ForeignKey(
        "education.TeacherGroupSubject",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Преподаватель предмета группы"),
    )
    course = models.ForeignKey(
        "course.Course",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Курс"),
    )
    course_lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.SET_NULL,
        related_name="schedule_patterns",
        null=True,
        blank=True,
        verbose_name=_("Занятие курса"),
    )
    title = models.CharField(
        _("Название"),
        max_length=255,
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
    starts_on = models.DateField(
        _("Действует с"),
        null=True,
        blank=True,
    )
    ends_on = models.DateField(
        _("Действует по"),
        null=True,
        blank=True,
    )
    repeat_rule = models.CharField(
        _("Правило повторения"),
        max_length=255,
        blank=True,
    )
    priority = models.PositiveSmallIntegerField(
        _("Приоритет"),
        default=100,
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_patterns"
        verbose_name = _("Шаблон занятия")
        verbose_name_plural = _("Шаблоны занятий")
        ordering = ("organization", "weekday", "time_slot", "group", "subject")
        indexes = [
            models.Index(fields=("organization", "academic_year", "is_active")),
            models.Index(fields=("organization", "weekday", "time_slot")),
            models.Index(fields=("group", "weekday", "time_slot")),
            models.Index(fields=("teacher", "weekday", "time_slot")),
            models.Index(fields=("room", "weekday", "time_slot")),
            models.Index(fields=("course", "course_lesson")),
            models.Index(fields=("status", "source_type")),
        ]

    def __str__(self) -> str:
        title = self.title or self.subject or self.course_lesson or _("Занятие")
        return f"{title} — {self.get_weekday_display()}, {self.time_slot}"

    def clean(self) -> None:
        super().clean()

        errors: dict[str, str] = {}

        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = _("Время окончания должно быть позже времени начала.")

        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            errors["ends_on"] = _("Дата окончания не может быть раньше даты начала.")

        if (
            self.course_lesson_id
            and self.course_id
            and self.course_lesson.course_id != self.course_id
        ):
            errors["course_lesson"] = _(
                "Занятие курса должно относиться к выбранному курсу."
            )

        if self.group_subject_id:
            if self.group_id and self.group_subject.group_id != self.group_id:
                errors["group_subject"] = _(
                    "Предмет группы должен относиться к выбранной группе."
                )

            if self.subject_id and self.group_subject.subject_id != self.subject_id:
                errors["group_subject"] = _(
                    "Предмет группы должен соответствовать выбранному предмету."
                )

        if errors:
            raise ValidationError(errors)
