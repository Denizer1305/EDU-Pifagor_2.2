from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    ReviewCommentCreateAPIView,
    SubmissionAnswerReviewAPIView,
    SubmissionReviewApproveAPIView,
    SubmissionReviewDetailAPIView,
    SubmissionReviewListAPIView,
    SubmissionReviewRejectAPIView,
    SubmissionReviewReturnForRevisionAPIView,
    SubmissionReviewStartAPIView,
    SubmissionReviewSubmitAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "submissions/<int:submission_id>/reviews/",
        SubmissionReviewListAPIView.as_view(),
        name="submission-review-list",
    ),
    path(
        "reviews/<int:pk>/",
        SubmissionReviewDetailAPIView.as_view(),
        name="submission-review-detail",
    ),
    path(
        "submissions/<int:submission_id>/reviews/start/",
        SubmissionReviewStartAPIView.as_view(),
        name="submission-review-start",
    ),
    path(
        "answers/<int:answer_id>/review/",
        SubmissionAnswerReviewAPIView.as_view(),
        name="submission-answer-review",
    ),
    path(
        "reviews/<int:review_id>/comments/",
        ReviewCommentCreateAPIView.as_view(),
        name="review-comment-create",
    ),
    # Совместимость со старым endpoint без review_id.
    path(
        "reviews/comments/",
        ReviewCommentCreateAPIView.as_view(),
        name="review-comment-create-flat",
    ),
    path(
        "reviews/<int:review_id>/submit/",
        SubmissionReviewSubmitAPIView.as_view(),
        name="submission-review-submit",
    ),
    path(
        "reviews/<int:review_id>/return/",
        SubmissionReviewReturnForRevisionAPIView.as_view(),
        name="submission-review-return",
    ),
    path(
        "reviews/<int:review_id>/approve/",
        SubmissionReviewApproveAPIView.as_view(),
        name="submission-review-approve",
    ),
    path(
        "reviews/<int:review_id>/reject/",
        SubmissionReviewRejectAPIView.as_view(),
        name="submission-review-reject",
    ),
]
