from __future__ import annotations

from django.urls import path

from apps.schedule.views.import_export import (
    ScheduleExportGroupAPIView,
    ScheduleExportPeriodAPIView,
    ScheduleExportRoomAPIView,
    ScheduleExportTeacherAPIView,
    ScheduleGenerationBatchDetailAPIView,
    ScheduleGenerationBatchListCreateAPIView,
    ScheduleImportApplyAPIView,
    ScheduleImportBatchDetailAPIView,
    ScheduleImportBatchListAPIView,
    ScheduleImportParseAPIView,
)

urlpatterns = [
    path(
        "imports/",
        ScheduleImportBatchListAPIView.as_view(),
        name="import-batch-list",
    ),
    path(
        "imports/<int:pk>/",
        ScheduleImportBatchDetailAPIView.as_view(),
        name="import-batch-detail",
    ),
    path(
        "imports/parse/",
        ScheduleImportParseAPIView.as_view(),
        name="import-parse",
    ),
    path(
        "imports/<int:pk>/apply/",
        ScheduleImportApplyAPIView.as_view(),
        name="import-apply",
    ),
    path(
        "generation-batches/",
        ScheduleGenerationBatchListCreateAPIView.as_view(),
        name="generation-batch-list-create",
    ),
    path(
        "generation-batches/<int:pk>/",
        ScheduleGenerationBatchDetailAPIView.as_view(),
        name="generation-batch-detail",
    ),
    path(
        "exports/groups/<int:group_id>/",
        ScheduleExportGroupAPIView.as_view(),
        name="export-group",
    ),
    path(
        "exports/teachers/<int:teacher_id>/",
        ScheduleExportTeacherAPIView.as_view(),
        name="export-teacher",
    ),
    path(
        "exports/rooms/<int:room_id>/",
        ScheduleExportRoomAPIView.as_view(),
        name="export-room",
    ),
    path(
        "exports/periods/<int:education_period_id>/",
        ScheduleExportPeriodAPIView.as_view(),
        name="export-period",
    ),
]
