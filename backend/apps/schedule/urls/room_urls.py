from __future__ import annotations

from django.urls import path

from apps.schedule.views.room import (
    ScheduleRoomArchiveAPIView,
    ScheduleRoomDetailAPIView,
    ScheduleRoomListCreateAPIView,
)

urlpatterns = [
    path(
        "rooms/",
        ScheduleRoomListCreateAPIView.as_view(),
        name="room-list-create",
    ),
    path(
        "rooms/<int:pk>/",
        ScheduleRoomDetailAPIView.as_view(),
        name="room-detail",
    ),
    path(
        "rooms/<int:pk>/archive/",
        ScheduleRoomArchiveAPIView.as_view(),
        name="room-archive",
    ),
]
