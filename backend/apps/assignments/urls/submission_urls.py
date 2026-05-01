from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    SubmissionAnswerSaveAPIView,
    SubmissionAttachFileAPIView,
    SubmissionDetailAPIView,
    SubmissionListAPIView,
    SubmissionRetryAPIView,
    SubmissionStartAPIView,
    SubmissionSubmitAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "submissions/",
        SubmissionListAPIView.as_view(),
        name="submission-list",
    ),
    path(
        "submissions/<int:pk>/",
        SubmissionDetailAPIView.as_view(),
        name="submission-detail",
    ),
    path(
        "submissions/start/",
        SubmissionStartAPIView.as_view(),
        name="submission-start",
    ),
    path(
        "submissions/<int:submission_id>/answers/",
        SubmissionAnswerSaveAPIView.as_view(),
        name="submission-answer-save",
    ),
    path(
        "submissions/<int:submission_id>/attachments/",
        SubmissionAttachFileAPIView.as_view(),
        name="submission-attach-file",
    ),
    path(
        "submissions/<int:submission_id>/submit/",
        SubmissionSubmitAPIView.as_view(),
        name="submission-submit",
    ),
    path(
        "submissions/<int:submission_id>/retry/",
        SubmissionRetryAPIView.as_view(),
        name="submission-retry",
    ),
]
