from __future__ import annotations

from django.urls import path

from apps.schedule.views.pattern import (
    SchedulePatternCopyAPIView,
    SchedulePatternDeactivateAPIView,
    SchedulePatternDetailAPIView,
    SchedulePatternListCreateAPIView,
)

urlpatterns = [
    path(
        "patterns/",
        SchedulePatternListCreateAPIView.as_view(),
        name="pattern-list-create",
    ),
    path(
        "patterns/<int:pk>/",
        SchedulePatternDetailAPIView.as_view(),
        name="pattern-detail",
    ),
    path(
        "patterns/<int:pk>/deactivate/",
        SchedulePatternDeactivateAPIView.as_view(),
        name="pattern-deactivate",
    ),
    path(
        "patterns/copy/",
        SchedulePatternCopyAPIView.as_view(),
        name="pattern-copy",
    ),
]
