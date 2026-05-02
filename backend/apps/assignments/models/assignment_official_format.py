from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class AssignmentOfficialFormat(TimeStampedModel):
    class OfficialFamilyChoices(models.TextChoices):
        NONE = "none", "Нет"
        VPR = "vpr", "ВПР"
        OGE = "oge", "ОГЭ"
        EGE = "ege", "ЕГЭ"
        GVE = "gve", "ГВЭ"
        FINAL_ESSAY = "final_essay", "Итоговое сочинение"
        FINAL_INTERVIEW = "final_interview", "Итоговое собеседование"
        DEMO_EXAM = "demo_exam", "Демоэкзамен"
        STATE_EXAM = "state_exam", "Государственный экзамен"

    class SourceKindChoices(models.TextChoices):
        OFFICIAL_DEMO = "official_demo", "Официальная демоверсия"
        OFFICIAL_ARCHIVE = "official_archive", "Официальный архив"
        TEACHER_ADAPTED = "teacher_adapted", "Адаптировано преподавателем"
        PLATFORM_GENERATED = "platform_generated", "Сгенерировано платформой"

    assignment = models.OneToOneField(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="official_format",
        verbose_name="Работа",
    )
    official_family = models.CharField(
        max_length=32,
        choices=OfficialFamilyChoices.choices,
        default=OfficialFamilyChoices.NONE,
        verbose_name="Официальный формат",
    )
    assessment_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Год",
    )
    grade_level = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Класс / курс",
    )
    exam_subject_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Наименование предмета",
    )
    source_kind = models.CharField(
        max_length=32,
        choices=SourceKindChoices.choices,
        default=SourceKindChoices.TEACHER_ADAPTED,
        verbose_name="Источник",
    )
    source_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Название источника",
    )
    source_url = models.URLField(
        blank=True,
        verbose_name="Ссылка на источник",
    )
    format_version = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Версия формата",
    )
    is_preparation_only = models.BooleanField(
        default=True,
        verbose_name="Только для подготовки",
    )
    has_answer_key = models.BooleanField(
        default=False,
        verbose_name="Есть ответы",
    )
    has_scoring_criteria = models.BooleanField(
        default=False,
        verbose_name="Есть критерии оценивания",
    )
    has_official_demo_source = models.BooleanField(
        default=False,
        verbose_name="Есть официальный источник",
    )

    class Meta:
        db_table = "assignments_assignment_official_format"
        verbose_name = "Официальный формат работы"
        verbose_name_plural = "Официальные форматы работ"

    def clean(self):
        errors: dict[str, str] = {}

        if (
            self.official_family != self.OfficialFamilyChoices.NONE
            and not self.is_preparation_only
        ):
            errors["is_preparation_only"] = (
                "Официальные форматы в системе используются только для подготовки."
            )

        if self.official_family in {
            self.OfficialFamilyChoices.VPR,
            self.OfficialFamilyChoices.OGE,
            self.OfficialFamilyChoices.EGE,
            self.OfficialFamilyChoices.GVE,
        }:
            if not self.assessment_year:
                errors["assessment_year"] = "Для выбранного формата нужно указать год."
            if not self.grade_level:
                errors["grade_level"] = "Для выбранного формата нужно указать класс."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.get_official_family_display()}: {self.assignment}"
