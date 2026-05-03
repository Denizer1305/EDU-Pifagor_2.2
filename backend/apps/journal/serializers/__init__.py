from __future__ import annotations

from apps.journal.serializers.attendance import (
    AttendanceRecordCreateSerializer,
    AttendanceRecordDetailSerializer,
    AttendanceRecordListSerializer,
    AttendanceRecordUpdateSerializer,
)
from apps.journal.serializers.grade import (
    JournalGradeCreateSerializer,
    JournalGradeDetailSerializer,
    JournalGradeListSerializer,
    JournalGradeUpdateSerializer,
)
from apps.journal.serializers.journal_lesson import (
    JournalLessonCreateSerializer,
    JournalLessonDetailSerializer,
    JournalLessonListSerializer,
    JournalLessonUpdateSerializer,
)
from apps.journal.serializers.summary import (
    JournalSummaryDetailSerializer,
    JournalSummaryListSerializer,
)
from apps.journal.serializers.topic_progress import (
    TopicProgressCreateSerializer,
    TopicProgressDetailSerializer,
    TopicProgressListSerializer,
    TopicProgressUpdateSerializer,
)

__all__ = (
    "AttendanceRecordCreateSerializer",
    "AttendanceRecordDetailSerializer",
    "AttendanceRecordListSerializer",
    "AttendanceRecordUpdateSerializer",
    "JournalGradeCreateSerializer",
    "JournalGradeDetailSerializer",
    "JournalGradeListSerializer",
    "JournalGradeUpdateSerializer",
    "JournalLessonCreateSerializer",
    "JournalLessonDetailSerializer",
    "JournalLessonListSerializer",
    "JournalLessonUpdateSerializer",
    "JournalSummaryDetailSerializer",
    "JournalSummaryListSerializer",
    "TopicProgressCreateSerializer",
    "TopicProgressDetailSerializer",
    "TopicProgressListSerializer",
    "TopicProgressUpdateSerializer",
)
