from __future__ import annotations

from django.urls import path

from apps.journal.views import (
    AttendanceRecordDetailAPIView,
    AttendanceRecordListCreateAPIView,
    JournalGradeDetailAPIView,
    JournalGradeListCreateAPIView,
    JournalLessonDetailAPIView,
    JournalLessonListCreateAPIView,
    JournalSummaryListAPIView,
    JournalSummaryRecalculateAPIView,
    TopicProgressListAPIView,
    TopicProgressSyncAPIView,
)

app_name = "journal"

urlpatterns = [
    # Занятия журнала
    path(
        "lessons/",
        JournalLessonListCreateAPIView.as_view(),
        name="lesson-list-create",
    ),
    path(
        "lessons/<int:pk>/",
        JournalLessonDetailAPIView.as_view(),
        name="lesson-detail",
    ),
    # Посещаемость
    path(
        "attendance/",
        AttendanceRecordListCreateAPIView.as_view(),
        name="attendance-list-create",
    ),
    path(
        "attendance/<int:pk>/",
        AttendanceRecordDetailAPIView.as_view(),
        name="attendance-detail",
    ),
    # Оценки
    path(
        "grades/",
        JournalGradeListCreateAPIView.as_view(),
        name="grade-list-create",
    ),
    path(
        "grades/<int:pk>/",
        JournalGradeDetailAPIView.as_view(),
        name="grade-detail",
    ),
    # Сводки журнала
    path(
        "summaries/",
        JournalSummaryListAPIView.as_view(),
        name="summary-list",
    ),
    path(
        "summaries/recalculate/",
        JournalSummaryRecalculateAPIView.as_view(),
        name="summary-recalculate",
    ),
    # Прогресс тем
    path(
        "topic-progress/",
        TopicProgressListAPIView.as_view(),
        name="topic-progress-list",
    ),
    path(
        "topic-progress/sync/",
        TopicProgressSyncAPIView.as_view(),
        name="topic-progress-sync",
    ),
]
