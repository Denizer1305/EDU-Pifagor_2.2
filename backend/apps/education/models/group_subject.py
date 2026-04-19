from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class GroupSubject(models.Model):
    """
    Учебный предмет группы.
    Фиксирует, какой предмет изучает конкретная группа
    в определенном учебном году и периоде.
    """

    class AssessmentTypeChoices(models.TextChoices):
        NONE = "none", _("Без аттестации")
        PASS_FAIL = "pass_fail", _("Зачет / незачет")
        CREDIT = "credit", _("Зачет")
        EXAM = "exam", _("Экзамен")
        TEST = "test", _("Тестирование")
        PROJECT = "project", _("Проект")
        OTHER = "other", _("Иная форма")

    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.CASCADE,
        related_name="group_subjects",
        verbose_name=_("Группа"),
    )
    subject = models.ForeignKey(
        "organizations.Subject",
        on_delete=models.PROTECT,
        related_name="group_subjects",
        verbose_name=_("Предмет"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.PROTECT,
        related_name="group_subjects",
        verbose_name=_("Учебный год"),
    )
    period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.PROTECT,
        related_name="group_subjects",
        verbose_name=_("Учебный период"),
    )

    planned_hours = models.PositiveIntegerField(
        _("Плановые часы"),
        default=0,
    )
    contact_hours = models.PositiveIntegerField(
        _("Контактные часы"),
        default=0,
    )
    independent_hours = models.PositiveIntegerField(
        _("Самостоятельная работа"),
        default=0,
    )
    assessment_type = models.CharField(
        _("Форма аттестации"),
        max_length=32,
        choices=AssessmentTypeChoices.choices,
        default=AssessmentTypeChoices.NONE,
    )

    is_required = models.BooleanField(
        _("Обязательный предмет"),
        default=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
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
        db_table = "education_group_subject"
        verbose_name = _("Предмет группы")
        verbose_name_plural = _("Предметы групп")
        ordering = ("group", "period__sequence", "subject")
        constraints = [
            models.UniqueConstraint(
                fields=("group", "subject", "academic_year", "period"),
                name="unique_group_subject_per_period",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.group} — {self.subject} — {self.period}"

    def clean(self) -> None:
        super().clean()

        if self.period.academic_year_id != self.academic_year_id:
            raise ValidationError(
                {"period": _("Учебный период должен принадлежать тому же учебному году.")}
            )

        if self.contact_hours > self.planned_hours:
            raise ValidationError(
                {"contact_hours": _("Контактные часы не могут превышать плановые часы.")}
            )
