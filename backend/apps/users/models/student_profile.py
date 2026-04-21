from __future__ import annotations

from django.db import models
from django.core.exceptions import ValidationError
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

    class VerificationStatusChoices(models.TextChoices):
        NOT_FILLED = "not_filled", _("Не заполнено")
        PENDING = "pending", _("Ожидает подтверждения")
        APPROVED = "approved", _("Подтверждено")
        REJECTED = "rejected", _("Отклонено")

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

    requested_organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        related_name="student_profile_requests",
        verbose_name=_("Запрошенная образовательная организация"),
        blank=True,
        null=True,
    )

    requested_department = models.ForeignKey(
        "organizations.Department",
        on_delete=models.SET_NULL,
        related_name="student_profile_requests",
        verbose_name=_("Запрошенное отделение"),
        blank=True,
        null=True,
    )
    requested_group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        related_name="student_profile_requests",
        verbose_name=_("Запрошенная группа"),
        blank=True,
        null=True,
    )
    submitted_group_code = models.CharField(
        _("Введенный код группы"),
        max_length=128,
        blank=True,
    )
    verification_status = models.CharField(
        _("Статус подтверждения"),
        max_length=32,
        choices=VerificationStatusChoices.choices,
        default=VerificationStatusChoices.NOT_FILLED,
    )
    verified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="verified_student_profiles",
        verbose_name=_("Подтвердил"),
        blank=True,
        null=True,
    )
    verified_at = models.DateTimeField(
        _("Дата подтверждения"),
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
        db_table = "users_student_profile"
        verbose_name = _("Профиль студента")
        verbose_name_plural = _("Профили студентов")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return self.user.full_name

    def clean(self) -> None:
        """Выполняет валидацию и нормализацию полей."""
        if self.submitted_group_code:
            self.submitted_group_code = self.submitted_group_code.strip()

        if self.verification_comment:
            self.verification_comment = self.verification_comment.strip()

        if (
            self.requested_department
            and self.requested_organization
            and self.requested_department.organization_id != self.requested_organization_id
        ):
            raise ValidationError(
                {"requested_department": _("Отделение должно принадлежать выбранной организации.")}
            )

        if (
            self.requested_group
            and self.requested_organization
            and self.requested_group.organization_id != self.requested_organization_id
        ):
            raise ValidationError(
                {"requested_group": _("Группа должна принадлежать выбранной организации.")}
            )

        if (
            self.requested_group
            and self.requested_department
            and self.requested_group.department_id
            and self.requested_group.department_id != self.requested_department_id
        ):
            raise ValidationError(
                {"requested_group": _("Группа должна принадлежать выбранному отделению.")}
            )
