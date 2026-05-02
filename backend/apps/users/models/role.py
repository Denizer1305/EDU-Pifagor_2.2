from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    Роль пользователя на платформе.
    Не заменяет системные поля Django is_staff / is_superuser
    """

    code = models.CharField(
        _("Код роли"),
        max_length=10,
        unique=True,
        db_index=True,
        help_text=_("Системные роли: admin, teacher, student, parent."),
    )
    name = models.CharField(
        _("Название роли"),
        max_length=100,
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
        db_table = "users_roles"
        verbose_name = _("Роль")
        verbose_name_plural = _("Роли")
        ordering = ("id",)

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"{self.name} ({self.code})"
