from __future__ import annotations

from django.urls import URLPattern, URLResolver

from . import analytics_urls
from . import assignment_urls
from . import grade_urls
from . import publication_urls
from . import review_urls
from . import rubric_urls
from . import structure_urls
from . import submission_urls

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
