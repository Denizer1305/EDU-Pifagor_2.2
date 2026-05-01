from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.filters import GroupCuratorFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_group_curators_queryset
from apps.organizations.serializers import GroupCuratorSerializer
from apps.organizations.services import (
    assign_group_curator,
    remove_group_curator,
)

logger = logging.getLogger(__name__)


class GroupCuratorListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GroupCuratorSerializer
    filterset_class = GroupCuratorFilter
    search_fields = (
        "group__name",
        "group__code",
        "teacher__email",
        "teacher__profile__last_name",
    )
    ordering_fields = (
        "created_at",
        "starts_at",
        "ends_at",
    )

    def get_queryset(self):
        logger.info("GroupCuratorListView.get_queryset called")
        return get_group_curators_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("GroupCuratorListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        curator = assign_group_curator(
            group=serializer.validated_data["group"],
            teacher=serializer.validated_data["teacher"],
            is_primary=serializer.validated_data.get("is_primary", True),
            is_active=serializer.validated_data.get("is_active", True),
            starts_at=serializer.validated_data.get("starts_at"),
            ends_at=serializer.validated_data.get("ends_at"),
            notes=serializer.validated_data.get("notes", ""),
        )

        output_serializer = self.get_serializer(curator)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GroupCuratorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GroupCuratorSerializer

    def get_queryset(self):
        logger.info("GroupCuratorDetailView.get_queryset called")
        return get_group_curators_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("GroupCuratorDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.get("group", instance.group)
        teacher = serializer.validated_data.get("teacher", instance.teacher)
        is_primary = serializer.validated_data.get("is_primary", instance.is_primary)
        is_active = serializer.validated_data.get("is_active", instance.is_active)
        starts_at = serializer.validated_data.get("starts_at", instance.starts_at)
        ends_at = serializer.validated_data.get("ends_at", instance.ends_at)
        notes = serializer.validated_data.get("notes", instance.notes)

        curator = assign_group_curator(
            group=group,
            teacher=teacher,
            is_primary=is_primary,
            is_active=is_active,
            starts_at=starts_at,
            ends_at=ends_at,
            notes=notes,
        )

        output_serializer = self.get_serializer(curator)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("GroupCuratorDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info("GroupCuratorDetailView.destroy called")

        instance = self.get_object()
        remove_group_curator(
            group=instance.group,
            teacher=instance.teacher,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
