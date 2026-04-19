from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class TeacherGroupSubject(models.Model):
    """
    Закрепление преподавателя за предметом группы.
    Показывает, какой преподаватель ведет конкретный предмет у конкретной группы.
    """

    class RoleChoices(models.TextChoices):
        PRIMARY = "primary", _("Основной преподаватель")
        ASSISTANT = "assistant", _("Ассистент")
        SUBSTITUTE = "substitute", _("Замещающий преподаватель")
        OTHER = "other", _("Иная роль")

    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_group_subjects",
        verbose_name=_("Преподаватель"),
    )
    group_subject = models.ForeignKey(
        "education.GroupSubject",
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
        verbose_name=_("Предмет группы"),
    )

    role = models.CharField(
        _("Роль преподавателя"),
        max_length=32,
        choices=RoleChoices.choices,
        default=RoleChoices.PRIMARY,
    )
    is_primary = models.BooleanField(
        _("Основной преподаватель"),
        default=True,
    )
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
    )

    planned_hours = models.PositiveIntegerField(
        _("Плановые часы преподавателя"),
        default=0,
    )

    starts_at = models.DateField(
        _("Дата начала"),
        blank=True,
        null=True,
    )
    ends_at = models.DateField(
        _("Дата окончания"),
        blank=True,
        null=True,
    )

    notes = models.TextField(
        _("Примечание"),
        blank=True,
    )

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
    )

    class Meta:
        db_table = "education_teacher_group_subject"
        verbose_name = _("Закрепление преподавателя за предметом группы")
        verbose_name_plural = _("Закрепления преподавателей за предметами групп")
        ordering = ("group_subject", "teacher")
        constraints = [
            models.UniqueConstraint(
                fields=("teacher", "group_subject"),
                name="unique_teacher_group_subject_assignment",
            ),
            models.UniqueConstraint(
                fields=("group_subject", "is_primary"),
                condition=Q(is_primary=True),
                name="unique_primary_teacher_per_group_subject",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.teacher.full_name} — {self.group_subject}"

    def clean(self) -> None:
        super().clean()

        period = self.group_subject.period

        if self.ends_at and self.starts_at and self.ends_at < self.starts_at:
            raise ValidationError(
                {"ends_at": _("Дата окончания не может быть раньше даты начала.")}
            )

        if self.starts_at and self.starts_at < period.start_date:
            raise ValidationError(
                {"starts_at": _("Дата начала не может быть раньше начала учебного периода.")}
            )

        if self.ends_at and self.ends_at > period.end_date:
            raise ValidationError(
                {"ends_at": _("Дата окончания не может быть позже окончания учебного периода.")}
            )
