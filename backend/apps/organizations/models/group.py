from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.organizations.validators import validate_academic_year, validate_group_code, validate_year_order

class Group(models.Model):
    """
    Учебная группа.
    Через группу студенты связываются с образовательной организацией и учебным процессом.
    """

    class StudyFormChoices(models.TextChoices):
        FULL_TIME = (
            "full_time", _("Очная"),
        )
        PART_TIME = (
            "part_time", _("Очно-заочная"),
        )
        DISTANCE = (
            "distance", _("Дистанционная"),
        )
        EXTRAMURAL = (
            "extramural", _("Заочная"),
        )
        OTHER = (
            "other", _("Иная"),
        )

    class StatusChoices(models.TextChoices):
        ACTIVE = (
            "active", _("Активна"),
        )
        ARCHIVED = (
            "archived", _("Архивирована"),
        )
        GRADUATED = (
            "graduated", _("Выпущена"),
        )
        CLOSED = (
            "closed", _("Закрыта"),
        )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="groups",
        verbose_name=_("Организация"),
    )
    department = models.ForeignKey(
        "organizations.Department",
        on_delete=models.SET_NULL,
        related_name="groups",
        verbose_name=_("Подразделение"),
        blank=True,
        null=True,
    )

    name = models.CharField(
        _("Название группы"),
        max_length=255,
    )
    code = models.CharField(
        _("Код группы"),
        max_length=64,
        db_index=True,
        validators=[validate_group_code],
    )

    study_form = models.CharField(
        _("Форма обучения"),
        max_length=32,
        choices=StudyFormChoices.choices,
        default=StudyFormChoices.FULL_TIME,
    )
    course_number = models.PositiveSmallIntegerField(
        _("Курс / год обучения"),
        blank=True,
        null=True,
    )
    admission_year = models.PositiveIntegerField(
        _("Год набора"),
        blank=True,
        null=True,
    )
    graduation_year = models.PositiveIntegerField(
        _("Год выпуска"),
        blank=True,
        null=True,
    )
    academic_year = models.CharField(
        _("Учебный год"),
        max_length=32,
        blank=True,
        help_text=_("Например: 2025/2026"),
        validators=[validate_academic_year],
    )

    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )

    description = models.TextField(
        _("Описание"),
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
        db_table = "organizations_group"
        verbose_name = _("Учебная группа")
        verbose_name_plural = _("Учебные группы")
        ordering = (
            "organization", "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "organization", "code",
                ),
                name="unique_group_code_per_organization",
            ),
            models.UniqueConstraint(
                fields=(
                    "organization", "name",
                ),
                name="unique_group_name_per_organization",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.organization} — {self.name}"

    def clean(self) -> None:
        super().clean()

        validate_year_order(
            admission_year=self.admission_year,
            graduation_year=self.graduation_year,
        )

        if self.department and self.department.organization_id != self.organization_id:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {"department": _("Подразделение должно принадлежать той же организации, что и группа.")}
            )
