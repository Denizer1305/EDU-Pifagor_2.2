from __future__ import annotations

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """
    Образовательная организация.
    Представляет школу, колледж, вуз или иной учебный центр в системе.

    Также хранит код регистрации преподавателя:
    в базе сохраняется только хеш кода, а не его исходное значение.
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

    teacher_registration_code_hash = models.CharField(
        _("Хеш кода регистрации преподавателя"),
        max_length=255,
        blank=True,
    )
    teacher_registration_code_is_active = models.BooleanField(
        _("Код регистрации преподавателя активен"),
        default=False,
    )
    teacher_registration_code_expires_at = models.DateTimeField(
        _("Код регистрации преподавателя действует до"),
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
        ordering = ("name",)

    def __str__(self) -> str:
        return self.short_name or self.name

    @property
    def has_active_teacher_registration_code(self) -> bool:
        """
        Есть ли у организации активный код регистрации преподавателя.
        """
        if not self.teacher_registration_code_hash:
            return False

        if not self.teacher_registration_code_is_active:
            return False

        if (
            self.teacher_registration_code_expires_at
            and self.teacher_registration_code_expires_at <= timezone.now()
        ):
            return False

        return True

    def set_teacher_registration_code(
        self,
        raw_code: str,
        *,
        expires_at=None,
    ) -> None:
        """
        Устанавливает новый код регистрации преподавателя.
        В базе сохраняется только его хеш.
        """
        raw_code = (raw_code or "").strip()
        if not raw_code:
            raise ValidationError(
                {"teacher_registration_code": _("Код регистрации преподавателя не может быть пустым.")}
            )

        self.teacher_registration_code_hash = make_password(raw_code)
        self.teacher_registration_code_is_active = True
        self.teacher_registration_code_expires_at = expires_at

    def clear_teacher_registration_code(self) -> None:
        """
        Полностью очищает код регистрации преподавателя.
        """
        self.teacher_registration_code_hash = ""
        self.teacher_registration_code_is_active = False
        self.teacher_registration_code_expires_at = None

    def disable_teacher_registration_code(self) -> None:
        """
        Деактивирует текущий код без удаления хеша.
        """
        self.teacher_registration_code_is_active = False

    def verify_teacher_registration_code(self, raw_code: str) -> bool:
        """
        Проверяет введённый код регистрации преподавателя.
        """
        raw_code = (raw_code or "").strip()

        if not raw_code:
            return False

        if not self.has_active_teacher_registration_code:
            return False

        return check_password(raw_code, self.teacher_registration_code_hash)

    def clean(self) -> None:
        super().clean()

        if (
            self.teacher_registration_code_expires_at
            and self.teacher_registration_code_expires_at <= timezone.now()
            and self.teacher_registration_code_is_active
        ):
            raise ValidationError(
                {
                    "teacher_registration_code_expires_at": _(
                        "Срок действия кода регистрации преподавателя должен быть в будущем."
                    )
                }
            )
