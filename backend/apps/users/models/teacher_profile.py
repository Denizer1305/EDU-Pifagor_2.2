from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class TeacherProfile(models.Model):
    """
    Профиль преподавателя.

    Содержит только данные преподавателя.
    Предметы, организации и прочие свзяи хранить в отдельных моделях.
    """

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
        return self.user.full_name
