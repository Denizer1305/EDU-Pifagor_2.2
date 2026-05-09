from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    AssignmentAudienceListCreateAPIView,
    AssignmentPublicationArchiveAPIView,
    AssignmentPublicationCloseAPIView,
    AssignmentPublicationDetailAPIView,
    AssignmentPublicationListCreateAPIView,
    AssignmentPublicationPublishAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "publications/",
        AssignmentPublicationListCreateAPIView.as_view(),
        name="assignment-publication-list-create",
    ),
    path(
        "publications/<int:pk>/",
        AssignmentPublicationDetailAPIView.as_view(),
        name="assignment-publication-detail",
    ),
    path(
        "publications/<int:pk>/publish/",
        AssignmentPublicationPublishAPIView.as_view(),
        name="assignment-publication-publish",
    ),
    path(
        "publications/<int:pk>/close/",
        AssignmentPublicationCloseAPIView.as_view(),
        name="assignment-publication-close",
    ),
    path(
        "publications/<int:pk>/archive/",
        AssignmentPublicationArchiveAPIView.as_view(),
        name="assignment-publication-archive",
    ),
    path(
        "publications/<int:publication_id>/audiences/",
        AssignmentAudienceListCreateAPIView.as_view(),
        name="assignment-audience-list-create",
    ),
]
