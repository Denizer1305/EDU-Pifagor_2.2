from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.filters import OrganizationTypeFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_organization_types_queryset
from apps.organizations.serializers import OrganizationTypeSerializer
from apps.organizations.services import (
    create_organization_type,
    update_organization_type,
)

logger = logging.getLogger(__name__)


class OrganizationTypeListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationTypeSerializer
    filterset_class = OrganizationTypeFilter
    search_fields = (
        "code",
        "name",
    )
    ordering_fields = (
        "name",
        "created_at",
    )

    def get_queryset(self):
        logger.info("OrganizationTypeListView.get_queryset called")
        return get_organization_types_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("OrganizationTypeListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization_type = create_organization_type(
            code=serializer.validated_data["code"],
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(organization_type)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrganizationTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationTypeSerializer

    def get_queryset(self):
        logger.info("OrganizationTypeDetailView.get_queryset called")
        return get_organization_types_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("OrganizationTypeDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        organization_type = update_organization_type(
            organization_type=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(organization_type)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("OrganizationTypeDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
