from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.filters import (
    DepartmentFilter,
    OrganizationFilter,
    OrganizationTypeFilter,
)
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import (
    get_departments_queryset,
    get_organizations_queryset,
    get_organization_types_queryset,
)
from apps.organizations.serializers import (
    DepartmentSerializer,
    OrganizationSerializer,
    OrganizationTeacherRegistrationCodeSerializer,
    OrganizationTypeSerializer,
)
from apps.organizations.services import (
    clear_teacher_registration_code,
    create_department,
    create_organization,
    create_organization_type,
    disable_teacher_registration_code,
    set_teacher_registration_code,
    update_department,
    update_organization,
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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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


class OrganizationTeacherRegistrationCodeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info("OrganizationTeacherRegistrationCodeView.post called organization_id=%s", pk)
        organization = get_organizations_queryset().filter(pk=pk).first()
        if organization is None:
            return Response({"detail": "Организация не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrganizationTeacherRegistrationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = set_teacher_registration_code(
            organization=organization,
            raw_code=serializer.validated_data["teacher_registration_code"],
            expires_at=serializer.validated_data.get("teacher_registration_code_expires_at"),
        )

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk, *args, **kwargs):
        logger.info("OrganizationTeacherRegistrationCodeView.delete called organization_id=%s", pk)
        organization = get_organizations_queryset().filter(pk=pk).first()
        if organization is None:
            return Response({"detail": "Организация не найдена."}, status=status.HTTP_404_NOT_FOUND)

        organization = clear_teacher_registration_code(organization=organization)
        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )


class OrganizationTeacherRegistrationCodeDisableView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info("OrganizationTeacherRegistrationCodeDisableView.post called organization_id=%s", pk)
        organization = get_organizations_queryset().filter(pk=pk).first()
        if organization is None:
            return Response({"detail": "Организация не найдена."}, status=status.HTTP_404_NOT_FOUND)

        organization = disable_teacher_registration_code(organization=organization)
        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )


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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
