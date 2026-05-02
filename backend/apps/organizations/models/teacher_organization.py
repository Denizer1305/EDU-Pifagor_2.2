from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TeacherOrganization(models.Model):
    """
    Связь преподавателя с образовательной организацией.
    Позволяет закрепить преподавателя за одной или несколькими организациями.
    """

    class EmploymentTypeChoices(models.TextChoices):
        MAIN = ("main", _("Основное место работы"))
        PART_TIME = ("part_time", _("Совместительство"))
        CONTRACT = ("contract", _("Договор"))
        OTHER = ("other", _("Иное"))

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

    position = models.CharField(
        _("Должность"),
        max_length=255,
        blank=True,
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
        ordering = ("organization", "teacher")
        constraints = [
            models.UniqueConstraint(
                fields=("teacher", "organization"),
                name="unique_teacher_organization_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.teacher.full_name} — {self.organization}"

    @property
    def is_current(self) -> bool:
        """
        Является ли связь действующей на текущую дату.
        """
        if not self.is_active:
            return False

        today = timezone.localdate()

        if self.starts_at and self.starts_at > today:
            return False

        if self.ends_at and self.ends_at < today:
            return False

        return True

    def clean(self) -> None:
        super().clean()

        if self.ends_at and self.starts_at and self.ends_at < self.starts_at:
            raise ValidationError(
                {"ends_at": _("Дата окончания не может быть раньше даты начала.")}
            )

        if self.teacher_id and hasattr(self.teacher, "registration_type"):
            if self.teacher.registration_type != "teacher":
                raise ValidationError(
                    {
                        "teacher": _(
                            "Связь с организацией может быть создана только для пользователя с типом регистрации teacher."
                        )
                    }
                )

        if self.is_primary and not self.is_active:
            raise ValidationError(
                {"is_primary": _("Основная организация должна быть активной.")}
            )

        if self.is_primary and self.teacher_id:
            queryset = self.__class__.objects.filter(
                teacher_id=self.teacher_id,
                is_primary=True,
                is_active=True,
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            if queryset.exists():
                raise ValidationError(
                    {
                        "is_primary": _(
                            "У преподавателя уже есть другая основная активная организация."
                        )
                    }
                )
