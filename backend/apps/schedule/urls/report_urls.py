from __future__ import annotations

from django.urls import path

from apps.schedule.views.reports import (
    ScheduleGroupReportAPIView,
    ScheduleRoomReportAPIView,
    ScheduleTeacherReportAPIView,
)

urlpatterns = [
    path(
        "reports/groups/",
        ScheduleGroupReportAPIView.as_view(),
        name="report-group",
    ),
    path(
        "reports/teachers/",
        ScheduleTeacherReportAPIView.as_view(),
        name="report-teacher",
    ),
    path(
        "reports/rooms/",
        ScheduleRoomReportAPIView.as_view(),
        name="report-room",
    ),
]
