from __future__ import annotations

from django.urls import path

from apps.schedule.views.change import (
    ScheduleChangeDetailAPIView,
    ScheduleChangeListAPIView,
)

urlpatterns = [
    path(
        "changes/",
        ScheduleChangeListAPIView.as_view(),
        name="change-list",
    ),
    path(
        "changes/<int:pk>/",
        ScheduleChangeDetailAPIView.as_view(),
        name="change-detail",
    ),
]
