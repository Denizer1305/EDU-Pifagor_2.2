from __future__ import annotations

from django.urls import include, path

app_name = "schedule"

urlpatterns = [
    path("", include("apps.schedule.urls.room_urls")),
    path("", include("apps.schedule.urls.calendar_urls")),
    path("", include("apps.schedule.urls.slot_urls")),
    path("", include("apps.schedule.urls.pattern_urls")),
    path("", include("apps.schedule.urls.lesson_urls")),
    path("", include("apps.schedule.urls.change_urls")),
    path("", include("apps.schedule.urls.conflict_urls")),
    path("", include("apps.schedule.urls.import_export_urls")),
    path("", include("apps.schedule.urls.report_urls")),
]
