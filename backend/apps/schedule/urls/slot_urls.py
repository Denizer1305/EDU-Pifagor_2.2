from __future__ import annotations

from django.urls import path

from apps.schedule.views.time_slot import (
    ScheduleTimeSlotBulkCreateAPIView,
    ScheduleTimeSlotDetailAPIView,
    ScheduleTimeSlotListCreateAPIView,
)

urlpatterns = [
    path(
        "time-slots/",
        ScheduleTimeSlotListCreateAPIView.as_view(),
        name="time-slot-list-create",
    ),
    path(
        "time-slots/<int:pk>/",
        ScheduleTimeSlotDetailAPIView.as_view(),
        name="time-slot-detail",
    ),
    path(
        "time-slots/bulk-create-default/",
        ScheduleTimeSlotBulkCreateAPIView.as_view(),
        name="time-slot-bulk-create-default",
    ),
]
