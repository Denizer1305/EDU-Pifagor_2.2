from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.journal.models import JournalGrade
from apps.journal.models.choices import GradeScale, GradeType


class JournalGradeAdminForm(forms.ModelForm):
    """Форма оценки для админки с правилами российской системы оценивания."""

    class Meta:
        model = JournalGrade
        fields = "__all__"  # noqa: DJ007

    def clean(self) -> dict:
        cleaned_data = super().clean()

        scale = cleaned_data.get("scale")
        grade_type = cleaned_data.get("grade_type")
        score_five = cleaned_data.get("score_five")
        is_passed = cleaned_data.get("is_passed")

        errors: dict[str, ValidationError] = {}

        if scale == GradeScale.FIVE_POINT:
            if score_five is None:
                errors["score_five"] = ValidationError(
                    _("Для пятибалльной оценки укажите значение от 1 до 5.")
                )

            if is_passed is not None:
                errors["is_passed"] = ValidationError(
                    _("Для пятибалльной оценки поле зачёта должно быть пустым.")
                )

        if scale == GradeScale.PASS_FAIL:
            if is_passed is None:
                errors["is_passed"] = ValidationError(
                    _("Для зачёта укажите результат: зачёт или незачёт.")
                )

            if score_five is not None:
                errors["score_five"] = ValidationError(
                    _("Для зачёта пятибалльная оценка должна быть пустой.")
                )

        if grade_type == GradeType.CREDIT and scale != GradeScale.PASS_FAIL:
            errors["scale"] = ValidationError(
                _("Тип оценки «Зачёт» должен использовать шкалу зачёт/незачёт.")
            )

        if errors:
            raise ValidationError(errors)

        return cleaned_data
