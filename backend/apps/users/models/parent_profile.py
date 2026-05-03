from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class ParentProfile(models.Model):
    """
    Профиль родителя.
    Связи с детьми вынесены в отдельные сущности
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="parent_profile",
        verbose_name=_("Пользователь"),
    )

    occupation = models.CharField(
        _("Род деятельности"),
        max_length=255,
        blank=True,
    )

    work_place = models.CharField(
        _("Место работы"),
        max_length=255,
        blank=True,
    )

    emergency_contact_phone = models.CharField(
        _("Экстренный телефон для связи"),
        max_length=32,
        blank=True,
    )

    notes = models.TextField(
        _("Служебные заметки"),
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
        db_table = "users_parent_profile"
        verbose_name = _("Профиль родителя")
        verbose_name_plural = _("Профили родителей")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return self.user.full_name
