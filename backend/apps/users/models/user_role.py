from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.Model):
    """
    Связь: One-to-Many.
    Один пользовтаель может иметь несколько ролей.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("Пользователь"),
    )
    role = models.ForeignKey(
        "users.Role",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("Роль"),
    )
    assigned_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )

    class Meta:
        db_table = "users_user_role"
        verbose_name = _("Роль пользователя")
        verbose_name_plural = _("Роли пользователя")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "role"),
                name="unique_user_role",
            )
        ]
        ordering = ['-assigned_at']

    def __str__(self):
        return str(f"{self.user} - {self.role}")


