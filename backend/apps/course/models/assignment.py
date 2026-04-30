from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.course.models.base import TimeStampedModel, normalize_text


class CourseAssignment(TimeStampedModel):
    class AssignmentTypeChoices(models.TextChoices):
        GROUP = "group", "Назначение группе"
        STUDENT = "student", "Назначение студенту"

    class Meta:
        db_table = "course_assignment"
        verbose_name = "Назначение курса"
        verbose_name_plural = "Назначения курса"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("course", "group"),
                condition=Q(group__isnull=False),
                name="unique_course_group_assignment",
            ),
            models.UniqueConstraint(
                fields=("course", "student"),
                condition=Q(student__isnull=False),
                name="unique_course_student_assignment",
            ),
        ]
        indexes = [
            models.Index(fields=("course", "is_active")),
            models.Index(fields=("group",)),
            models.Index(fields=("student",)),
        ]

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Курс",
    )
    assignment_type = models.CharField(
        max_length=16,
        choices=AssignmentTypeChoices.choices,
        verbose_name="Тип назначения",
    )

    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="course_assignments",
        null=True,
        blank=True,
        verbose_name="Группа",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_assignments",
        null=True,
        blank=True,
        verbose_name="Студент",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_courses",
        verbose_name="Назначил",
    )

    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Доступ с",
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Доступ до",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
    )
    auto_enroll = models.BooleanField(
        default=True,
        verbose_name="Автоматически зачислять",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    def clean(self):
        errors = {}

        self.notes = normalize_text(self.notes)

        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            errors["ends_at"] = "Дата окончания доступа не может быть раньше даты начала."

        if self.assignment_type == self.AssignmentTypeChoices.GROUP:
            if not self.group:
                errors["group"] = "Для назначения группе нужно указать группу."
            if self.student:
                errors["student"] = "Для назначения группе нельзя указывать студента."

        if self.assignment_type == self.AssignmentTypeChoices.STUDENT:
            if not self.student:
                errors["student"] = "Для назначения студенту нужно указать студента."
            if self.group:
                errors["group"] = "Для назначения студенту нельзя указывать группу."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.notes = normalize_text(self.notes)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.group_id:
            return f"{self.course} → {self.group}"
        if self.student_id:
            return f"{self.course} → {self.student}"
        return f"{self.course}"
