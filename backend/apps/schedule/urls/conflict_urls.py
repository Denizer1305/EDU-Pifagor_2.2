from __future__ import annotations

from django.urls import path

from apps.schedule.views.conflict import (
    ScheduleConflictDetailAPIView,
    ScheduleConflictDetectLessonAPIView,
    ScheduleConflictDetectPatternAPIView,
    ScheduleConflictDetectPeriodAPIView,
    ScheduleConflictIgnoreAPIView,
    ScheduleConflictListAPIView,
    ScheduleConflictResolveAPIView,
)

urlpatterns = [
    path(
        "conflicts/",
        ScheduleConflictListAPIView.as_view(),
        name="conflict-list",
    ),
    path(
        "conflicts/<int:pk>/",
        ScheduleConflictDetailAPIView.as_view(),
        name="conflict-detail",
    ),
    path(
        "conflicts/<int:pk>/resolve/",
        ScheduleConflictResolveAPIView.as_view(),
        name="conflict-resolve",
    ),
    path(
        "conflicts/<int:pk>/ignore/",
        ScheduleConflictIgnoreAPIView.as_view(),
        name="conflict-ignore",
    ),
    path(
        "conflicts/detect/lesson/<int:lesson_id>/",
        ScheduleConflictDetectLessonAPIView.as_view(),
        name="conflict-detect-lesson",
    ),
    path(
        "conflicts/detect/pattern/<int:pattern_id>/",
        ScheduleConflictDetectPatternAPIView.as_view(),
        name="conflict-detect-pattern",
    ),
    path(
        "conflicts/detect/period/",
        ScheduleConflictDetectPeriodAPIView.as_view(),
        name="conflict-detect-period",
    ),
]
