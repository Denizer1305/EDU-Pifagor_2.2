from django.urls import path

from apps.feedback.views import (
    FeedbackErrorCreateAPIView,
    FeedbackRequestAdminDetailAPIView,
    FeedbackRequestAdminListAPIView,
    FeedbackRequestCreateAPIView,
    MyFeedbackRequestDetailAPIView,
    MyFeedbackRequestListAPIView,
)

app_name = "feedback"

urlpatterns = [
    path(
        "requests/",
        FeedbackRequestCreateAPIView.as_view(),
        name="feedback-request-create",
    ),
    path(
        "requests/error-report/",
        FeedbackErrorCreateAPIView.as_view(),
        name="feedback-error-create",
    ),
    path(
        "requests/my/",
        MyFeedbackRequestListAPIView.as_view(),
        name="my-feedback-request-list",
    ),
    path(
        "requests/my/<int:pk>/",
        MyFeedbackRequestDetailAPIView.as_view(),
        name="my-feedback-request-detail",
    ),
    path(
        "requests/admin/",
        FeedbackRequestAdminListAPIView.as_view(),
        name="admin-feedback-request-list",
    ),
    path(
        "requests/admin/<int:pk>/",
        FeedbackRequestAdminDetailAPIView.as_view(),
        name="admin-feedback-request-detail",
    ),
]
