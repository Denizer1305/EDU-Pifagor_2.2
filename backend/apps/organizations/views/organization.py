from __future__ import annotations

import logging

from rest_framework import generics

from apps.organizations.filters import DepartmentFilter, OrganizationFilter, OrganizationTypeFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import (
    get_departments_queryset,
    get_organizations_queryset,
    get_organization_types_queryset,
)
from apps.organizations.serializers import (
    DepartmentSerializer,
    OrganizationSerializer,
    OrganizationTypeSerializer,
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


class OrganizationTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationTypeSerializer

    def get_queryset(self):
        logger.info("OrganizationTypeDetailView.get_queryset called")
        return get_organization_types_queryset()


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


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        logger.info("OrganizationDetailView.get_queryset called")
        return get_organizations_queryset()


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


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        logger.info("DepartmentDetailView.get_queryset called")
        return get_departments_queryset()
