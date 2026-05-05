from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import AudienceType
from apps.schedule.models.base import ScheduleTimeStampedModel


class SchedulePatternAudience(ScheduleTimeStampedModel):
    pattern = models.ForeignKey(
        "schedule.SchedulePattern",
        on_delete=models.CASCADE,
        related_name="audiences",
        verbose_name=_("Шаблон занятия"),
    )
    audience_type = models.CharField(
        _("Тип аудитории"),
        max_length=32,
        choices=AudienceType.choices,
        default=AudienceType.GROUP,
        db_index=True,
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="schedule_pattern_audiences",
        null=True,
        blank=True,
        verbose_name=_("Группа"),
    )
    subgroup_name = models.CharField(
        _("Название подгруппы"),
        max_length=128,
        blank=True,
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="schedule_pattern_audiences_as_student",
        null=True,
        blank=True,
        verbose_name=_("Студент"),
    )
    course_enrollment = models.ForeignKey(
        "course.CourseEnrollment",
        on_delete=models.CASCADE,
        related_name="schedule_pattern_audiences",
        null=True,
        blank=True,
        verbose_name=_("Запись на курс"),
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_pattern_audiences"
        verbose_name = _("Аудитория шаблона занятия")
        verbose_name_plural = _("Аудитории шаблонов занятий")
        ordering = ("pattern", "audience_type", "group", "subgroup_name")
        indexes = [
            models.Index(fields=("pattern", "audience_type")),
            models.Index(fields=("group", "subgroup_name")),
            models.Index(fields=("student",)),
            models.Index(fields=("course_enrollment",)),
        ]

    def __str__(self) -> str:
        if self.group_id:
            return str(self.group)
        if self.student_id:
            return str(self.student)
        if self.course_enrollment_id:
            return str(self.course_enrollment)
        return self.get_audience_type_display()


class ScheduledLessonAudience(ScheduleTimeStampedModel):
    scheduled_lesson = models.ForeignKey(
        "schedule.ScheduledLesson",
        on_delete=models.CASCADE,
        related_name="audiences",
        verbose_name=_("Занятие расписания"),
    )
    audience_type = models.CharField(
        _("Тип аудитории"),
        max_length=32,
        choices=AudienceType.choices,
        default=AudienceType.GROUP,
        db_index=True,
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="scheduled_lesson_audiences",
        null=True,
        blank=True,
        verbose_name=_("Группа"),
    )
    subgroup_name = models.CharField(
        _("Название подгруппы"),
        max_length=128,
        blank=True,
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="scheduled_lesson_audiences_as_student",
        null=True,
        blank=True,
        verbose_name=_("Студент"),
    )
    course_enrollment = models.ForeignKey(
        "course.CourseEnrollment",
        on_delete=models.CASCADE,
        related_name="scheduled_lesson_audiences",
        null=True,
        blank=True,
        verbose_name=_("Запись на курс"),
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "scheduled_lesson_audiences"
        verbose_name = _("Аудитория занятия расписания")
        verbose_name_plural = _("Аудитории занятий расписания")
        ordering = ("scheduled_lesson", "audience_type", "group", "subgroup_name")
        indexes = [
            models.Index(fields=("scheduled_lesson", "audience_type")),
            models.Index(fields=("group", "subgroup_name")),
            models.Index(fields=("student",)),
            models.Index(fields=("course_enrollment",)),
        ]

    def __str__(self) -> str:
        if self.group_id:
            return str(self.group)
        if self.student_id:
            return str(self.student)
        if self.course_enrollment_id:
            return str(self.course_enrollment)
        return self.get_audience_type_display()
