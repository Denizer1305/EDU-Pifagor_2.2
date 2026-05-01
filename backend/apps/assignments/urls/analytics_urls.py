from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    AssignmentStatisticsAPIView,
    CourseAssignmentDashboardAPIView,
    PublicationStatisticsAPIView,
    StudentAssignmentProgressAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "analytics/assignments/<int:assignment_id>/statistics/",
        AssignmentStatisticsAPIView.as_view(),
        name="assignment-statistics",
    ),
    path(
        "analytics/publications/<int:publication_id>/statistics/",
        PublicationStatisticsAPIView.as_view(),
        name="publication-statistics",
    ),
    path(
        "analytics/assignments/<int:assignment_id>/students/<int:student_id>/progress/",
        StudentAssignmentProgressAPIView.as_view(),
        name="student-assignment-progress",
    ),
    path(
        "analytics/courses/<int:course_id>/dashboard/",
        CourseAssignmentDashboardAPIView.as_view(),
        name="course-assignment-dashboard",
    ),
]
