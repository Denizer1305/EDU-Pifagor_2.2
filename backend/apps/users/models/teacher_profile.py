from __future__ import annotations

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TeacherProfile(models.Model):
    """
    Профиль преподавателя.

    Содержит только данные преподавателя.
    Предметы, организации и прочие свзяи хранить в отдельных моделях.
    """

    class VerificationStatusChoices(models.TextChoices):
        NOT_VERIFIED = "not_verified", _("Не подтвержден")
        PENDING = "pending", _("Ожидает подтверждения")
        APPROVED = "approved", _("Подтвержден")
        REJECTED = "rejected", _("Отклонен")

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        verbose_name=_("Пользователь"),
    )
    public_title = models.CharField(
        _("Публичный заголовок"),
        max_length=255,
        blank=True,
        help_text=_('Например: "Преподаватель математики".')
    )
    short_bio = models.CharField(
        _("Краткое описание"),
        max_length=255,
        blank=True,
    )
    bio = models.TextField(
        _("Описание"),
        blank=True,
    )
    education = models.TextField(
        _("Образование"),
        blank=True,
    )

    experience = models.PositiveSmallIntegerField(
        _("Стаж (лет)"),
        blank=True,
        null=True,
    )

    achievements = models.TextField(
        _("Краткое описание достижений и наград"),
        blank=True,
        help_text=_("Короткий блок достижений для карточки преподавателя.")
    )

    cover_image = models.ImageField(
        _("Обложка карточки преподавателя"),
        upload_to="users/teachers/covers/",
        blank=True,
        null=True,
    )

    is_public = models.BooleanField(
        _("Публичный профиль"),
        default=True,
    )
    show_on_teachers_page = models.BooleanField(
        _("Показывать на странице преподавателей"),
        default=True,
    )

    requested_organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        related_name="teacher_profile_requests",
        verbose_name=_("Запрошенная образовательная организация"),
        blank=True,
        null=True,
    )

    requested_department = models.ForeignKey(
        "organizations.Department",
        on_delete=models.SET_NULL,
        related_name="teacher_profile_requests",
        verbose_name=_("Запрошенное подразделение"),
        blank=True,
        null=True,
    )

    verification_status = models.CharField(
        _("Статус подтверждения"),
        max_length=32,
        choices=VerificationStatusChoices.choices,
        default=VerificationStatusChoices.NOT_VERIFIED,
    )

    code_verified_at = models.DateTimeField(
        _("Дата подтверждения регистрационного кода"),
        blank=True,
        null=True,
    )

    verified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="verified_teacher_profiles",
        verbose_name=_("Подтвердил"),
        blank=True,
        null=True,
    )

    verified_at = models.DateTimeField(
        _("Дата окончательного подтверждения"),
        blank=True,
        null=True,
    )

    verification_comment = models.TextField(
        _("Комментарий проверки"),
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
        db_table = "users_teacher_profile"
        verbose_name = _("Профиль преподавателя")
        verbose_name_plural = _("Профили преподавателей")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return self.user.full_name

    def clean(self) -> None:
        """Выполняет валидацию и нормализацию полей."""
        if self.verification_comment:
            self.verification_comment = self.verification_comment.strip()

        if (
            self.requested_department
            and self.requested_organization
            and self.requested_department.organization_id != self.requested_organization_id
        ):
            raise ValidationError(
                {"requested_department": _("Подразделение должно принадлежать выбранной организации.")}
            )
