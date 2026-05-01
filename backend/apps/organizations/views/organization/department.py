from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.filters import DepartmentFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_departments_queryset
from apps.organizations.serializers import DepartmentSerializer
from apps.organizations.services import (
    create_department,
    update_department,
)

logger = logging.getLogger(__name__)


class DepartmentListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DepartmentSerializer
    filterset_class = DepartmentFilter
    search_fields = (
        "name",
        "short_name",
        "organization__name",
    )
    ordering_fields = (
        "name",
        "created_at",
    )

    def get_queryset(self):
        logger.info("DepartmentListView.get_queryset called")
        return get_departments_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("DepartmentListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        department = create_department(
            organization=serializer.validated_data["organization"],
            name=serializer.validated_data["name"],
            short_name=serializer.validated_data.get("short_name", ""),
            description=serializer.validated_data.get("description", ""),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(department)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        logger.info("DepartmentDetailView.get_queryset called")
        return get_departments_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("DepartmentDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        department = update_department(
            department=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(department)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("DepartmentDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
