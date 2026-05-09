from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class TeacherSubject(models.Model):
    """
    Связь преподавателя с учебным предметом.
    Используется для предметов преподавателя, фильтрации и отображения в карточке.
    """

    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="teacher_subjects",
        verbose_name=_("Преподаватель"),
    )
    subject = models.ForeignKey(
        "organizations.Subject",
        on_delete=models.CASCADE,
        related_name="teacher_links",
        verbose_name=_("Предмет"),
    )

    is_primary = models.BooleanField(
        _("Основной предмет"),
        default=False,
    )
    is_active = models.BooleanField(
        _("Активен"),
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
        db_table = "organizations_teacher_subject"
        verbose_name = _("Связь преподавателя с предметом")
        verbose_name_plural = _("Связи преподавателей с предметами")
        ordering = (
            "teacher",
            "subject",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "teacher",
                    "subject",
                ),
                name="unique_teacher_subject_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.teacher.full_name} — {self.subject}"
