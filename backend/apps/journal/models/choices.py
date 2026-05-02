from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class GradeType(models.TextChoices):
    CURRENT = "current", _("Текущая")
    HOMEWORK = "homework", _("Домашняя работа")
    TEST = "test", _("Тест")
    PRACTICAL = "practical", _("Практическая работа")
    LABORATORY = "laboratory", _("Лабораторная работа")
    CONTROL = "control", _("Контрольная работа")
    EXAM = "exam", _("Экзамен")
    CREDIT = "credit", _("Зачёт")
    FINAL = "final", _("Итоговая")


class GradeScale(models.TextChoices):
    FIVE_POINT = "five_point", _("Пятибалльная")
    PASS_FAIL = "pass_fail", _("Зачёт/незачёт")
