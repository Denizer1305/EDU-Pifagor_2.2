from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class GroupCurator(models.Model):
    """
    Куратор учебной группы.
    Выделен в отдельную сущность для гибкого управления кураторством и историей назначений.
    """

    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="curators",
        verbose_name=_("Группа"),
    )
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="curated_groups",
        verbose_name=_("Преподаватель"),
    )

    is_primary = models.BooleanField(
        _("Основной куратор"),
        default=True,
    )
    is_active = models.BooleanField(
        _("Активно"),
        default=True,
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
        db_table = "organizations_group_curator"
        verbose_name = _("Куратор группы")
        verbose_name_plural = _("Кураторы групп")
        ordering = ("-is_primary", "-is_active", "-starts_at", "-created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("group", "teacher"),
                name="unique_teacher_per_group_curatorship",
            )
        ]

    def __str__(self) -> str:
        return f"{self.group} — {self.teacher.full_name}"

    @property
    def is_current(self) -> bool:
        """
        Является ли кураторство текущим на текущую дату.
        """
        today = timezone.localdate()

        has_started = not self.starts_at or self.starts_at <= today
        has_not_ended = not self.ends_at or self.ends_at >= today

        return self.is_active and has_started and has_not_ended

    def clean(self) -> None:
        super().clean()

        if self.ends_at and self.starts_at and self.ends_at < self.starts_at:
            raise ValidationError(
                {"ends_at": _("Дата окончания не может быть раньше даты начала.")}
            )

        if (
            self.teacher_id
            and hasattr(self.teacher, "registration_type")
            and self.teacher.registration_type != "teacher"
        ):
            raise ValidationError(
                {
                    "teacher": _(
                        "Куратором группы может быть только пользователь с типом регистрации teacher."
                    )
                }
            )
