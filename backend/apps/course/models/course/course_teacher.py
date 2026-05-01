from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.course.models.base import TimeStampedModel


class CourseTeacher(TimeStampedModel):
    class RoleChoices(models.TextChoices):
        OWNER = "owner", "Владелец"
        TEACHER = "teacher", "Преподаватель"
        METHODIST = "methodist", "Методист"
        ASSISTANT = "assistant", "Ассистент"

    class Meta:
        db_table = "course_teacher"
        verbose_name = "Преподаватель курса"
        verbose_name_plural = "Преподаватели курса"
        ordering = ("course", "teacher")
        constraints = [
            models.UniqueConstraint(
                fields=("course", "teacher"),
                name="unique_course_teacher",
            ),
        ]

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="course_teachers",
        verbose_name="Курс",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_teacher_links",
        verbose_name="Преподаватель",
    )
    role = models.CharField(
        max_length=32,
        choices=RoleChoices.choices,
        default=RoleChoices.TEACHER,
        verbose_name="Роль",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    can_edit = models.BooleanField(
        default=True,
        verbose_name="Может редактировать курс",
    )
    can_manage_structure = models.BooleanField(
        default=True,
        verbose_name="Может управлять структурой",
    )
    can_manage_assignments = models.BooleanField(
        default=False,
        verbose_name="Может назначать курс",
    )
    can_view_analytics = models.BooleanField(
        default=True,
        verbose_name="Может смотреть аналитику",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Назначен",
    )

    def __str__(self) -> str:
        return f"{self.course} — {self.teacher}"
