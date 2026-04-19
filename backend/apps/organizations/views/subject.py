from __future__ import annotations

import logging

from rest_framework import generics

from apps.organizations.filters import SubjectCategoryFilter, SubjectFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import (
    get_subject_categories_queryset,
    get_subjects_queryset,
)
from apps.organizations.serializers import (
    SubjectCategorySerializer,
    SubjectSerializer,
)


logger = logging.getLogger(__name__)

class SubjectCategoryListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SubjectCategorySerializer
    filterset_class = SubjectCategoryFilter
    search_fields = (
        "code",
        "name",
    )
    ordering_fields = (
        "name",
        "created_at",
    )

    def get_queryset(self):
        logger.info("SubjectCategoryListView.get_queryset called")
        return get_subject_categories_queryset()


class SubjectCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SubjectCategorySerializer

    def get_queryset(self):
        logger.info("SubjectCategoryDetailView.get_queryset called")
        return get_subject_categories_queryset()


class SubjectListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SubjectSerializer
    filterset_class = SubjectFilter
    search_fields = (
        "name",
        "short_name",
        "category__name",
    )
    ordering_fields = (
        "name",
        "created_at",
    )

    def get_queryset(self):
        logger.info("SubjectListView.get_queryset called")
        return get_subjects_queryset()


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SubjectSerializer

    def get_queryset(self):
        logger.info("SubjectDetailView.get_queryset called")
        return get_subjects_queryset()
