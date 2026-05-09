from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    AssignmentArchiveAPIView,
    AssignmentDetailAPIView,
    AssignmentDuplicateAPIView,
    AssignmentListCreateAPIView,
    AssignmentPublishAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "assignments/",
        AssignmentListCreateAPIView.as_view(),
        name="assignment-list-create",
    ),
    path(
        "assignments/<int:pk>/",
        AssignmentDetailAPIView.as_view(),
        name="assignment-detail",
    ),
    path(
        "assignments/<int:pk>/publish/",
        AssignmentPublishAPIView.as_view(),
        name="assignment-publish",
    ),
    path(
        "assignments/<int:pk>/archive/",
        AssignmentArchiveAPIView.as_view(),
        name="assignment-archive",
    ),
    path(
        "assignments/<int:pk>/duplicate/",
        AssignmentDuplicateAPIView.as_view(),
        name="assignment-duplicate",
    ),
]
