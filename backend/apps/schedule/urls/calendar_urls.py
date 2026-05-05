from __future__ import annotations

from django.urls import path

from apps.schedule.views.calendar import (
    ScheduleCalendarDetailAPIView,
    ScheduleCalendarListCreateAPIView,
    ScheduleCalendarMarkHolidayAPIView,
    ScheduleCalendarMarkPracticeAPIView,
    ScheduleCalendarMarkVacationAPIView,
    ScheduleWeekTemplateDetailAPIView,
    ScheduleWeekTemplateListCreateAPIView,
)

urlpatterns = [
    path(
        "calendars/",
        ScheduleCalendarListCreateAPIView.as_view(),
        name="calendar-list-create",
    ),
    path(
        "calendars/<int:pk>/",
        ScheduleCalendarDetailAPIView.as_view(),
        name="calendar-detail",
    ),
    path(
        "calendars/mark-holiday/",
        ScheduleCalendarMarkHolidayAPIView.as_view(),
        name="calendar-mark-holiday",
    ),
    path(
        "calendars/mark-vacation/",
        ScheduleCalendarMarkVacationAPIView.as_view(),
        name="calendar-mark-vacation",
    ),
    path(
        "calendars/mark-practice/",
        ScheduleCalendarMarkPracticeAPIView.as_view(),
        name="calendar-mark-practice",
    ),
    path(
        "week-templates/",
        ScheduleWeekTemplateListCreateAPIView.as_view(),
        name="week-template-list-create",
    ),
    path(
        "week-templates/<int:pk>/",
        ScheduleWeekTemplateDetailAPIView.as_view(),
        name="week-template-detail",
    ),
]
