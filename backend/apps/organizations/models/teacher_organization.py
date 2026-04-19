from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class TeacherOrganization(models.Model):
    """
    Связь преподавателя с образовательной организацией.
    Позволяет закрепить преподавателя за одной или несколькими организациями.
    """

    class EmploymentTypeChoices(models.TextChoices):
        MAIN = (
            "main", _("Основное место работы"),
        )
        PART_TIME = (
            "part_time", _("Совместительство"),
        )
        CONTRACT = (
            "contract", _("Договор"),
        )
        OTHER = (
            "other", _("Иное"),
        )

    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_organizations",
        verbose_name=_("Преподаватель"),
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="teacher_links",
        verbose_name=_("Организация"),
    )

    employment_type = models.CharField(
        _("Тип занятости"),
        max_length=32,
        choices=EmploymentTypeChoices.choices,
        default=EmploymentTypeChoices.MAIN,
    )
    is_primary = models.BooleanField(
        _("Основная организация"),
        default=False,
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

    is_active = models.BooleanField(
        _("Активна"),
        default=True,
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
        db_table = "organizations_teacher_organization"
        verbose_name = _("Связь преподавателя с организацией")
        verbose_name_plural = _("Связи преподавателей с организациями")
        ordering = (
            "organization", "teacher",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "teacher", "organization",
                ),
                name="unique_teacher_organization_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.teacher.full_name} — {self.organization}"

    def clean(self) -> None:
        super().clean()

        if self.ends_at and self.starts_at and self.ends_at < self.starts_at:
            raise ValidationError(
                {"ends_at": _("Дата окончания не может быть раньше даты начала.")}
            )
