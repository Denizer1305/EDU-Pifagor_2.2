from __future__ import annotations

from django.urls import path

from apps.schedule.views.lesson import (
    ScheduledLessonCancelAPIView,
    ScheduledLessonChangeRoomAPIView,
    ScheduledLessonDetailAPIView,
    ScheduledLessonListCreateAPIView,
    ScheduledLessonLockAPIView,
    ScheduledLessonPublishAPIView,
    ScheduledLessonReplaceTeacherAPIView,
    ScheduledLessonRescheduleAPIView,
    ScheduledLessonUnlockAPIView,
)

urlpatterns = [
    path(
        "lessons/",
        ScheduledLessonListCreateAPIView.as_view(),
        name="lesson-list-create",
    ),
    path(
        "lessons/<int:pk>/",
        ScheduledLessonDetailAPIView.as_view(),
        name="lesson-detail",
    ),
    path(
        "lessons/<int:pk>/publish/",
        ScheduledLessonPublishAPIView.as_view(),
        name="lesson-publish",
    ),
    path(
        "lessons/<int:pk>/cancel/",
        ScheduledLessonCancelAPIView.as_view(),
        name="lesson-cancel",
    ),
    path(
        "lessons/<int:pk>/reschedule/",
        ScheduledLessonRescheduleAPIView.as_view(),
        name="lesson-reschedule",
    ),
    path(
        "lessons/<int:pk>/replace-teacher/",
        ScheduledLessonReplaceTeacherAPIView.as_view(),
        name="lesson-replace-teacher",
    ),
    path(
        "lessons/<int:pk>/change-room/",
        ScheduledLessonChangeRoomAPIView.as_view(),
        name="lesson-change-room",
    ),
    path(
        "lessons/<int:pk>/lock/",
        ScheduledLessonLockAPIView.as_view(),
        name="lesson-lock",
    ),
    path(
        "lessons/<int:pk>/unlock/",
        ScheduledLessonUnlockAPIView.as_view(),
        name="lesson-unlock",
    ),
]
