from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class AttendanceStatus(models.TextChoices):
    """Статус посещаемости студента на занятии."""

    PRESENT = "present", _("Присутствовал")
    ABSENT = "absent", _("Отсутствовал")
    LATE = "late", _("Опоздал")
    EXCUSED = "excused", _("Уважительная причина")
    REMOTE = "remote", _("Дистанционно")


class AttendanceRecord(models.Model):
    """
    Запись о посещаемости студента на конкретном занятии.

    Одна запись = один студент + одно занятие.
    Уникальность обеспечивается ограничением на уровне БД.
    """

    lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name=_("Занятие"),
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name=_("Студент"),
    )
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        verbose_name=_("Статус"),
        db_index=True,
    )
    comment = models.CharField(
        max_length=512,
        blank=True,
        verbose_name=_("Комментарий"),
    )

    # --- Служебные поля ---
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = _("Запись посещаемости")
        verbose_name_plural = _("Записи посещаемости")
        db_table = "journal_attendance_record"
        ordering = ["lesson__date", "student"]
        indexes = [
            models.Index(fields=["lesson", "status"], name="idx_attend_lesson_status"),
            models.Index(fields=["student", "status"], name="idx_attend_student_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "student"],
                name="uniq_attend_lesson_student",
            )
        ]

    def __str__(self) -> str:
        return f"{self.lesson} | {self.student} | {self.get_status_display()}"

    @property
    def is_absent(self) -> bool:
        return self.status == AttendanceStatus.ABSENT

    @property
    def is_present(self) -> bool:
        return self.status in (AttendanceStatus.PRESENT, AttendanceStatus.REMOTE)
