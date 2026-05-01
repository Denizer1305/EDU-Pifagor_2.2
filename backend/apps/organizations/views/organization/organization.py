from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.filters import OrganizationFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_organizations_queryset
from apps.organizations.serializers import OrganizationSerializer
from apps.organizations.services import (
    create_organization,
    update_organization,
)

logger = logging.getLogger(__name__)


class OrganizationListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    search_fields = (
        "name",
        "short_name",
        "city",
        "email",
    )
    ordering_fields = (
        "name",
        "created_at",
    )

    def get_queryset(self):
        logger.info("OrganizationListView.get_queryset called")
        return get_organizations_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("OrganizationListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = create_organization(
            type=serializer.validated_data["type"],
            name=serializer.validated_data["name"],
            short_name=serializer.validated_data.get("short_name", ""),
            description=serializer.validated_data.get("description", ""),
            city=serializer.validated_data.get("city", ""),
            address=serializer.validated_data.get("address", ""),
            phone=serializer.validated_data.get("phone", ""),
            email=serializer.validated_data.get("email", ""),
            website=serializer.validated_data.get("website", ""),
            logo=serializer.validated_data.get("logo"),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(organization)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        logger.info("OrganizationDetailView.get_queryset called")
        return get_organizations_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("OrganizationDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        organization = update_organization(
            organization=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(organization)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("OrganizationDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
