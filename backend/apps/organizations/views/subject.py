from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

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
from apps.organizations.services import (
    create_subject,
    create_subject_category,
    update_subject,
    update_subject_category,
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

    def create(self, request, *args, **kwargs):
        logger.info("SubjectCategoryListView.create called")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subject_category = create_subject_category(
            code=serializer.validated_data["code"],
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(subject_category)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class SubjectCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SubjectCategorySerializer

    def get_queryset(self):
        logger.info("SubjectCategoryDetailView.get_queryset called")
        return get_subject_categories_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("SubjectCategoryDetailView.update called")
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        subject_category = update_subject_category(
            subject_category=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(subject_category)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("SubjectCategoryDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


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

    def create(self, request, *args, **kwargs):
        logger.info("SubjectListView.create called")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subject = create_subject(
            category=serializer.validated_data["category"],
            name=serializer.validated_data["name"],
            short_name=serializer.validated_data.get("short_name", ""),
            description=serializer.validated_data.get("description", ""),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(subject)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = SubjectSerializer

    def get_queryset(self):
        logger.info("SubjectDetailView.get_queryset called")
        return get_subjects_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("SubjectDetailView.update called")
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        subject = update_subject(
            subject=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(subject)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("SubjectDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
