from __future__ import annotations

from apps.journal.admin.attendance import AttendanceRecordAdmin
from apps.journal.admin.grades import JournalGradeAdmin
from apps.journal.admin.lessons import JournalLessonAdmin
from apps.journal.admin.summaries import JournalSummaryAdmin
from apps.journal.admin.topics import TopicProgressAdmin

__all__ = (
    "AttendanceRecordAdmin",
    "JournalGradeAdmin",
    "JournalLessonAdmin",
    "JournalSummaryAdmin",
    "TopicProgressAdmin",
)
