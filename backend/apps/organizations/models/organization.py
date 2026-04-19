from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """
    Образовательная организация.
    Представляет школу, колледж, вуз или иной учебный центр в системе.
    """

    type = models.ForeignKey(
        "organizations.OrganizationType",
        on_delete=models.PROTECT,
        related_name="organizations",
        verbose_name=_("Тип организации"),
    )

    name = models.CharField(
        _("Полное название"),
        max_length=255,
        unique=True,
    )
    short_name = models.CharField(
        _("Краткое название"),
        max_length=255,
        blank=True,
    )

    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    city = models.CharField(
        _("Город"),
        max_length=150,
        blank=True,
    )
    address = models.CharField(
        _("Адрес"),
        max_length=255,
        blank=True,
    )

    phone = models.CharField(
        _("Телефон"),
        max_length=32,
        blank=True,
    )
    email = models.EmailField(
        _("Email"),
        blank=True,
    )
    website = models.URLField(
        _("Сайт"),
        blank=True,
    )

    logo = models.ImageField(
        _("Логотип"),
        upload_to="organizations/logos/",
        blank=True,
        null=True,
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
        db_table = "organizations_organization"
        verbose_name = _("Образовательная организация")
        verbose_name_plural = _("Образовательные организации")
        ordering = (
            "name",
        )

    def __str__(self) -> str:
        return self.short_name or self.name
