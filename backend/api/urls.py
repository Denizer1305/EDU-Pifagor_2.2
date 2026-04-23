from django.urls import include, path

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("organizations/", include("apps.organizations.urls")),
    path("education/", include("apps.education.urls")),
    path("course/", include("apps.course.urls")),
    path("content/", include("apps.content.urls")),
    path("assignments/", include("apps.assignments.urls")),
    path("testing/", include("apps.testing.urls")),
    path("schedule/", include("apps.schedule.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("analytics/", include("apps.analytics.urls")),
]
