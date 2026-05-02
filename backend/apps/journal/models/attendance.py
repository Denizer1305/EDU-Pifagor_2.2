from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AttendanceRecord(models.Model):
    """Посещаемость студента на конкретном занятии."""

    class AttendanceStatus(models.TextChoices):
        PRESENT = "present", _("Присутствовал")
        ABSENT = "absent", _("Отсутствовал")
        LATE = "late", _("Опоздал")
        EXCUSED = "excused", _("Отсутствовал по уважительной причине")
        REMOTE = "remote", _("Присутствовал дистанционно")

    lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.CASCADE,
        related_name="attendance_records",
        verbose_name=_("Занятие"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journal_attendance_records",
        verbose_name=_("Студент"),
    )
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
        db_index=True,
        verbose_name=_("Статус посещаемости"),
    )
    comment = models.CharField(
        max_length=512,
        blank=True,
        verbose_name=_("Комментарий"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления"),
    )

    class Meta:
        db_table = "journal_attendance_record"
        verbose_name = _("Запись посещаемости")
        verbose_name_plural = _("Посещаемость")
        ordering = ["lesson", "student"]
        indexes = [
            models.Index(
                fields=["lesson", "status"],
                name="idx_attend_lesson_status",
            ),
            models.Index(
                fields=["student", "status"],
                name="idx_attend_student_status",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "student"],
                name="uniq_attend_lesson_student",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student} — {self.lesson} — {self.get_status_display()}"

    @property
    def counts_as_attended(self) -> bool:
        return self.status in {
            self.AttendanceStatus.PRESENT,
            self.AttendanceStatus.LATE,
            self.AttendanceStatus.REMOTE,
        }

    @property
    def is_absence(self) -> bool:
        return self.status in {
            self.AttendanceStatus.ABSENT,
            self.AttendanceStatus.EXCUSED,
        }
