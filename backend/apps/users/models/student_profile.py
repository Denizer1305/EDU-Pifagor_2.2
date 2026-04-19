from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class StudentProfile(models.Model):
    """
    Профиль студента.
    Академические связи (группа, организация, курсы) должны жить в специализированных приложении.
    """

    class StudentStatusChoices(models.TextChoices):
        ACTIVE = (
            'active', _('Активный'),
        )
        ACADEMIC_LEAD = (
            'academic_lead', _('Академический отпуск'),
        )
        TRAMSFERRED = (
            'tramsferred', _('Переведен'),
        )
        GRADUATED = (
            'graduated', _('Выпустился'),
        )
        ARCHIVED = (
            'archived', _('В архиве'),
        )
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="student_profile",
        verbose_name=_("Пользователь"),
    )
    student_code = models.CharField(
        _("Код студента"),
        max_length=64,
        blank=True,
        help_text=_("Внутренний код студента в обр.организации, зависит от группы. "
                    "Например: ИП-4-01")
    )
    admission_year = models.PositiveSmallIntegerField(
        _("Год постпуления"),
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("Статус студента"),
        max_length=32,
        choices=StudentStatusChoices.choices,
        default=StudentStatusChoices.ACTIVE,
    )

    notes = models.TextField(
        _("Служебные заметки"),
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
        db_table = "users_student_profile"
        verbose_name = _("Профиль студента")
        verbose_name_plural = _("Профили студентов")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return self.user.full_name
