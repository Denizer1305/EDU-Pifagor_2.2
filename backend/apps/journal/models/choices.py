from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class JournalLessonStatus(models.TextChoices):
    PLANNED = "planned", _("Запланировано")
    CONDUCTED = "conducted", _("Проведено")
    CANCELLED = "cancelled", _("Отменено")


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", _("Присутствовал")
    ABSENT = "absent", _("Отсутствовал")
    LATE = "late", _("Опоздал")
    EXCUSED = "excused", _("Отсутствовал по уважительной причине")


class GradeScale(models.TextChoices):
    FIVE_POINT = "five_point", _("Пятибалльная")
    PASS_FAIL = "pass_fail", _("Зачёт/незачёт")


class GradeType(models.TextChoices):
    # Обычная текущая работа
    CURRENT = "current", _("Текущая")
    CLASSWORK = "classwork", _("Работа на занятии")
    BOARD_WORK = "board_work", _("Работа у доски")
    ORAL_ANSWER = "oral_answer", _("Устный ответ")
    HOMEWORK = "homework", _("Домашняя работа")

    # Проверочные форматы
    TEST = "test", _("Тест")
    QUIZ = "quiz", _("Проверочная работа")
    INDEPENDENT_WORK = "independent_work", _("Самостоятельная работа")
    CONTROL_WORK = "control_work", _("Контрольная работа")

    # Практико-ориентированные форматы
    PRACTICAL_WORK = "practical_work", _("Практическая работа")
    LABORATORY_WORK = "laboratory_work", _("Лабораторная работа")
    PROJECT = "project", _("Проектная работа")

    # Итоговые формы контроля
    CREDIT = "credit", _("Зачёт")
    EXAM = "exam", _("Экзамен")
    FINAL = "final", _("Итоговая")


class TopicProgressStatus(models.TextChoices):
    PLANNED = "planned", _("Запланирована")
    IN_PROGRESS = "in_progress", _("В процессе")
    COMPLETED = "completed", _("Пройдена")
    BEHIND = "behind", _("Есть отставание")
    SKIPPED = "skipped", _("Пропущена")
