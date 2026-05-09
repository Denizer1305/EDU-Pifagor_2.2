from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.filters import GroupFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_groups_queryset
from apps.organizations.serializers import GroupSerializer
from apps.organizations.services import (
    create_group,
    update_group,
)

logger = logging.getLogger(__name__)


class GroupListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GroupSerializer
    filterset_class = GroupFilter
    search_fields = (
        "name",
        "code",
        "organization__name",
        "department__name",
    )
    ordering_fields = (
        "name",
        "created_at",
        "admission_year",
    )

    def get_queryset(self):
        logger.info("GroupListView.get_queryset called")
        return get_groups_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("GroupListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = create_group(
            organization=serializer.validated_data["organization"],
            department=serializer.validated_data.get("department"),
            name=serializer.validated_data["name"],
            code=serializer.validated_data["code"],
            study_form=serializer.validated_data.get("study_form"),
            course_number=serializer.validated_data.get("course_number"),
            admission_year=serializer.validated_data.get("admission_year"),
            graduation_year=serializer.validated_data.get("graduation_year"),
            academic_year=serializer.validated_data.get("academic_year", ""),
            status=serializer.validated_data.get("status"),
            description=serializer.validated_data.get("description", ""),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(group)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GroupSerializer

    def get_queryset(self):
        logger.info("GroupDetailView.get_queryset called")
        return get_groups_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("GroupDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        group = update_group(
            group=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(group)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("GroupDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
