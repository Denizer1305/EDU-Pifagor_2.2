from django.urls import include, path

from config.settings.base import env_bool

urlpatterns = [
    path("users/", include("apps.users.urls")),
    path("organizations/", include("apps.organizations.urls")),
    path("education/", include("apps.education.urls")),
    path("course/", include("apps.course.urls")),
    path("assignments/", include("apps.assignments.urls")),
    path("feedback/", include("apps.feedback.urls")),
    path("journal/", include("apps.journal.urls")),
    path("schedule/", include("apps.schedule.urls")),
    path("notifications/", include("apps.notifications.urls")),
]

if env_bool("ENABLE_CONTENT_API", False):
    urlpatterns += [path("content/", include("apps.content.urls"))]

if env_bool("ENABLE_TESTING_API", False):
    urlpatterns += [path("testing/", include("apps.testing.urls"))]

if env_bool("ENABLE_ANALYTICS_API", False):
    urlpatterns += [path("analytics/", include("apps.analytics.urls"))]
