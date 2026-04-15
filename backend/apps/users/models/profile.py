from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """
    Общий профиль пользователя.
    Здесь лежат базовые данные, не привязанные к роли пользовальталя
    """

    class GenderChoices(models.TextChoices):
        MALE = 'male', _('Мужской')
        FEMALE = 'female', _('Женский')
        NOT_SPECIFIED = 'not_specified', _("Не указан")

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Пользователь"),
    )
    last_name = models.CharField(
        _("Фамилия"),
        max_length=150,
    )
    first_name = models.CharField(
        _("Имя"),
        max_length=150,
    )
    patronymic = models.CharField(
        _("Отчество"),
        max_length=150,
        blank=True,
    )

    phone = models.CharField(
        _("Телефон"),
        max_length=32,
    )
    birth_date = models.DateField(
        _("Дата рождения"),
        blank=True,
        null=True,
    )
    gender = models.CharField(
        _("Пол"),
        choices=GenderChoices.choices,
        default=GenderChoices.NOT_SPECIFIED,
        max_length=20,
    )
    avatar = models.ImageField(
        _("Аватар"),
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    about = models.TextField(
        _("О себе"),
        blank=True,
    )
    city = models.CharField(
        _("Город"),
        max_length=150,
        blank=True,
    )
    timezone = models.CharField(
        _("Часовой пояс"),
        max_length=150,
        blank=True,
        default="Europe/Moscow",
    )

    social_link_max = models.URLField(
        _("Ссылка на профиль в мессенджер MAX"),
        blank=True,
        null=True,
    )

    social_link_vk = models.URLField(
        _("Ссылка на профиль в ВКонтакте"),
        blank=True,
        null=True,
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
        db_table = "users_profile"
        verbose_name = _("Профиль")
        verbose_name_plural = _("Профили")
        ordering = ("last_name", "first_name", "patronymic")

    def __str__(self) -> str:
        return self.full_name

    @property
    def short_name(self) -> str:
        initials = []
        if self.first_name:
            initials.append(f"{self.first_name[0]}.")
        if self.patronymic:
            initials.append(f"{self.patronymic[0]}.")
        initials_str = " ".join(initials)
        return f"{self.last_name} {initials_str}".strip()

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(part for part in parts if part).strip()

    def clean(self) -> None:
        super().clean()

        if not self.first_name:
            raise ValidationError({"first_name": _("Имя обязательно.")})
        if not self.last_name:
            raise ValidationError({"last_name": _("Фамилия обязательна.")})
