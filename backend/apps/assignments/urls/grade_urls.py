from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    GradeRecordCreateFromSubmissionAPIView,
    GradeRecordDetailAPIView,
    GradeRecordListAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "grades/",
        GradeRecordListAPIView.as_view(),
        name="grade-list",
    ),
    path(
        "grades/<int:pk>/",
        GradeRecordDetailAPIView.as_view(),
        name="grade-detail",
    ),
    path(
        "submissions/<int:submission_id>/grade/",
        GradeRecordCreateFromSubmissionAPIView.as_view(),
        name="grade-create-from-submission",
    ),

    # Совместимость со старыми именами.
    path(
        "grade-records/",
        GradeRecordListAPIView.as_view(),
        name="grade-record-list",
    ),
    path(
        "grade-records/<int:pk>/",
        GradeRecordDetailAPIView.as_view(),
        name="grade-record-detail",
    ),
    path(
        "submissions/<int:submission_id>/grade-record/",
        GradeRecordCreateFromSubmissionAPIView.as_view(),
        name="grade-record-create-from-submission",
    ),
]
