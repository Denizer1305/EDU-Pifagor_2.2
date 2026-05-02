from __future__ import annotations

from django.urls import URLPattern, URLResolver

from . import (
    analytics_urls,
    assignment_urls,
    grade_urls,
    publication_urls,
    review_urls,
    rubric_urls,
    structure_urls,
    submission_urls,
)

app_name = "assignments"

urlpatterns: list[URLPattern | URLResolver] = [
    *assignment_urls.urlpatterns,
    *structure_urls.urlpatterns,
    *publication_urls.urlpatterns,
    *submission_urls.urlpatterns,
    *review_urls.urlpatterns,
    *rubric_urls.urlpatterns,
    *grade_urls.urlpatterns,
    *analytics_urls.urlpatterns,
]
