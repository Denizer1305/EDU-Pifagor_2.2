from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from apps.assignments.views import (
    RubricCriteriaReorderAPIView,
    RubricCriterionDetailAPIView,
    RubricCriterionListCreateAPIView,
    RubricDetailAPIView,
    RubricListCreateAPIView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "rubrics/",
        RubricListCreateAPIView.as_view(),
        name="rubric-list-create",
    ),
    # Совместимость: рубрики конкретной работы.
    path(
        "assignments/<int:assignment_id>/rubrics/",
        RubricListCreateAPIView.as_view(),
        name="assignment-rubric-list-create",
    ),
    path(
        "rubrics/<int:pk>/",
        RubricDetailAPIView.as_view(),
        name="rubric-detail",
    ),
    path(
        "rubrics/<int:rubric_id>/criteria/",
        RubricCriterionListCreateAPIView.as_view(),
        name="rubric-criterion-list-create",
    ),
    path(
        "criteria/<int:pk>/",
        RubricCriterionDetailAPIView.as_view(),
        name="rubric-criterion-detail",
    ),
    path(
        "rubrics/<int:rubric_id>/criteria/reorder/",
        RubricCriteriaReorderAPIView.as_view(),
        name="rubric-criteria-reorder",
    ),
]
