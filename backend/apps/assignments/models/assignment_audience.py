from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class AssignmentAudience(TimeStampedModel):
    class AudienceTypeChoices(models.TextChoices):
        ALL_COURSE_STUDENTS = "all_course_students", "Все студенты курса"
        GROUP = "group", "Группа"
        STUDENT = "student", "Студент"
        SELECTED_STUDENTS = "selected_students", "Выбранные студенты"

    publication = models.ForeignKey(
        "assignments.AssignmentPublication",
        on_delete=models.CASCADE,
        related_name="audiences",
        verbose_name="Публикация",
    )
    audience_type = models.CharField(
        max_length=32,
        choices=AudienceTypeChoices.choices,
        verbose_name="Тип аудитории",
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="assignment_audiences",
        null=True,
        blank=True,
        verbose_name="Группа",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_audiences",
        null=True,
        blank=True,
        verbose_name="Студент",
    )
    course_enrollment = models.ForeignKey(
        "course.CourseEnrollment",
        on_delete=models.CASCADE,
        related_name="assignment_audiences",
        null=True,
        blank=True,
        verbose_name="Запись на курс",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
    )

    class Meta:
        db_table = "assignments_assignment_audience"
        verbose_name = "Аудитория работы"
        verbose_name_plural = "Аудитории работ"
        indexes = [
            models.Index(fields=("publication", "audience_type")),
            models.Index(fields=("group",)),
            models.Index(fields=("student",)),
            models.Index(fields=("course_enrollment",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        if self.audience_type == self.AudienceTypeChoices.GROUP and not self.group_id:
            errors["group"] = "Для групповой аудитории нужно указать группу."

        if self.audience_type == self.AudienceTypeChoices.STUDENT and not self.student_id:
            errors["student"] = "Для персональной аудитории нужно указать студента."

        if self.audience_type == self.AudienceTypeChoices.SELECTED_STUDENTS and not self.student_id:
            errors["student"] = "Для выбранных студентов нужно указать студента."

        if self.course_enrollment_id and self.publication.course_id:
            if self.course_enrollment.course_id != self.publication.course_id:
                errors["course_enrollment"] = "Запись на курс должна относиться к курсу публикации."

        if self.student_id and self.course_enrollment_id:
            if self.course_enrollment.student_id != self.student_id:
                errors["course_enrollment"] = "Запись на курс должна принадлежать выбранному студенту."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.get_audience_type_display()} — {self.publication}"
