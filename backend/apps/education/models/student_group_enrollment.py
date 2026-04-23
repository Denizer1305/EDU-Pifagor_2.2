from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class StudentGroupEnrollment(models.Model):
    """
    Зачисление студента в учебную группу.
    Хранит академическую историю перемещений студента между группами.
    """

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", _("Активно")
        TRANSFERRED = "transferred", _("Переведен")
        SUSPENDED = "suspended", _("Приостановлено")
        GRADUATED = "graduated", _("Завершено")
        EXPELLED = "expelled", _("Отчислен")
        ARCHIVED = "archived", _("Архивировано")

    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="student_group_enrollments",
        verbose_name=_("Студент"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="student_enrollments",
        verbose_name=_("Группа"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.PROTECT,
        related_name="student_enrollments",
        verbose_name=_("Учебный год"),
    )

    enrollment_date = models.DateField(
        _("Дата зачисления"),
    )
    completion_date = models.DateField(
        _("Дата завершения / выбытия"),
        blank=True,
        null=True,
    )

    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
    )
    is_primary = models.BooleanField(
        _("Основное зачисление"),
        default=True,
    )

    journal_number = models.PositiveIntegerField(
        _("Номер в журнале"),
        blank=True,
        null=True,
    )
    notes = models.TextField(
        _("Примечание"),
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
        db_table = "education_student_group_enrollment"
        verbose_name = _("Зачисление студента в группу")
        verbose_name_plural = _("Зачисления студентов в группы")
        ordering = ("-academic_year__start_date", "group", "student")
        constraints = [
            models.UniqueConstraint(
                fields=("student", "group", "academic_year"),
                name="unique_student_group_enrollment_per_year",
            ),
            models.UniqueConstraint(
                fields=("student", "academic_year", "is_primary"),
                condition=Q(is_primary=True),
                name="unique_primary_student_enrollment_per_year",
            ),
            models.UniqueConstraint(
                fields=("group", "academic_year", "journal_number"),
                condition=Q(journal_number__isnull=False),
                name="unique_journal_number_per_group_and_year",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} — {self.group} — {self.academic_year}"

    def clean(self) -> None:
        super().clean()

        errors: dict[str, str] = {}

        if self.completion_date and self.completion_date < self.enrollment_date:
            errors["completion_date"] = _(
                "Дата завершения не может быть раньше даты зачисления."
            )

        if self.enrollment_date < self.academic_year.start_date:
            errors["enrollment_date"] = _(
                "Дата зачисления не может быть раньше начала учебного года."
            )

        if self.enrollment_date > self.academic_year.end_date:
            errors["enrollment_date"] = _(
                "Дата зачисления не может быть позже окончания учебного года."
            )

        if self.completion_date and self.completion_date > self.academic_year.end_date:
            errors["completion_date"] = _(
                "Дата завершения не может быть позже окончания учебного года."
            )

        if self.student_id:
            registration_type = getattr(self.student, "registration_type", "")
            if registration_type and registration_type != "student":
                errors["student"] = _(
                    "Зачисление в группу может быть создано только для пользователя с типом регистрации student."
                )

            is_email_verified = getattr(self.student, "is_email_verified", None)
            if is_email_verified is False:
                errors["student"] = _(
                    "Нельзя зачислить студента с неподтвержденной электронной почтой."
                )

            onboarding_status = getattr(self.student, "onboarding_status", "")
            if onboarding_status and onboarding_status != "active":
                errors["student"] = _(
                    "Нельзя зачислить студента с незавершенным онбордингом."
                )

            student_profile = getattr(self.student, "student_profile", None)
            if student_profile is not None:
                verification_status = getattr(student_profile, "verification_status", "")
                if verification_status and verification_status != "approved":
                    errors["student"] = _(
                        "Нельзя зачислить студента без подтвержденного студенческого профиля."
                    )

        if self.group_id:
            if hasattr(self.group, "is_active") and not self.group.is_active:
                errors["group"] = _("Нельзя зачислить студента в неактивную группу.")

            group_academic_year = getattr(self.group, "academic_year", "")
            if group_academic_year and group_academic_year != self.academic_year.name:
                errors["academic_year"] = _(
                    "Учебный год зачисления должен совпадать с учебным годом группы."
                )

        if self.status == self.StatusChoices.ACTIVE and self.completion_date:
            errors["status"] = _(
                "Активное зачисление не может иметь дату завершения."
            )

        if self.status != self.StatusChoices.ACTIVE and not self.completion_date:
            errors["completion_date"] = _(
                "Для завершенного, переведенного, архивного, приостановленного или отчисленного зачисления требуется дата завершения."
            )

        if errors:
            raise ValidationError(errors)
