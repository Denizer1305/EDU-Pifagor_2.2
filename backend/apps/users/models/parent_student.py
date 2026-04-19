from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ParentStudent(models.Model):
    """Модель parent student."""
    class RelationType(models.TextChoices):
        MOTHER = (
            "mother", _("Мать"),
        )
        FATHER = (
            "father", _("Отец"),
        )
        GUARDIAN = (
            "guardian", _("Опекун"),
        )
        REPRESENTATIVE = (
            "representative", _("Законный представитель"),
        )
        OTHER = (
            "other", _("Иное"),
        )

    parent = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="parent_student_links",
        verbose_name=_("Родитель"),
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="student_parent_links",
        verbose_name=_("Студент"),
    )

    relation_type = models.CharField(
        _("Тип связи"),
        max_length=32,
        choices=RelationType.choices,
        default=RelationType.OTHER,
    )

    is_primary = models.BooleanField(
        _("Основной представитель"),
        default=False,
    )

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )

    class Meta:
        db_table = "users_parent_student"
        verbose_name = _("Связь родитель-студент")
        verbose_name_plural = _("Связи родитель-студент")
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "parent", "student",
                ),
                name="unique_parent_student_link",
            )
        ]
        ordering = (
            "-is_primary", "-created_at",
        )

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"{self.parent.full_name} → {self.student.full_name}"

    def clean(self) -> None:
        """Выполняет валидацию и нормализацию полей."""
        super().clean()

        if self.parent_id == self.student_id:
            raise ValidationError(_("Нельзя связать пользователя с самим собой."))
