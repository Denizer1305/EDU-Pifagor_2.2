from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.filters import TeacherOrganizationFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_teacher_organizations_queryset
from apps.organizations.serializers import TeacherOrganizationSerializer
from apps.organizations.services import (
    assign_teacher_to_organization,
    remove_teacher_from_organization,
    set_primary_teacher_organization,
)

logger = logging.getLogger(__name__)


class TeacherOrganizationListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TeacherOrganizationSerializer
    filterset_class = TeacherOrganizationFilter
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "organization__name",
    )
    ordering_fields = (
        "created_at",
        "starts_at",
        "ends_at",
    )

    def get_queryset(self):
        logger.info("TeacherOrganizationListView.get_queryset called")
        return get_teacher_organizations_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("TeacherOrganizationListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        link = assign_teacher_to_organization(
            teacher=serializer.validated_data["teacher"],
            organization=serializer.validated_data["organization"],
            position=serializer.validated_data.get("position", ""),
            employment_type=serializer.validated_data.get("employment_type"),
            is_primary=serializer.validated_data.get("is_primary", False),
            starts_at=serializer.validated_data.get("starts_at"),
            ends_at=serializer.validated_data.get("ends_at"),
            notes=serializer.validated_data.get("notes", ""),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(link)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TeacherOrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TeacherOrganizationSerializer

    def get_queryset(self):
        logger.info("TeacherOrganizationDetailView.get_queryset called")
        return get_teacher_organizations_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("TeacherOrganizationDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        teacher = serializer.validated_data.get("teacher", instance.teacher)
        organization = serializer.validated_data.get(
            "organization",
            instance.organization,
        )
        position = serializer.validated_data.get("position", instance.position)
        employment_type = serializer.validated_data.get(
            "employment_type",
            instance.employment_type,
        )
        is_primary = serializer.validated_data.get("is_primary", instance.is_primary)
        starts_at = serializer.validated_data.get("starts_at", instance.starts_at)
        ends_at = serializer.validated_data.get("ends_at", instance.ends_at)
        notes = serializer.validated_data.get("notes", instance.notes)
        is_active = serializer.validated_data.get("is_active", instance.is_active)

        link = assign_teacher_to_organization(
            teacher=teacher,
            organization=organization,
            position=position,
            employment_type=employment_type,
            is_primary=is_primary,
            starts_at=starts_at,
            ends_at=ends_at,
            notes=notes,
            is_active=is_active,
        )

        output_serializer = self.get_serializer(link)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("TeacherOrganizationDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info("TeacherOrganizationDetailView.destroy called")

        instance = self.get_object()
        remove_teacher_from_organization(
            teacher=instance.teacher,
            organization=instance.organization,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherOrganizationSetPrimaryView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info(
            "TeacherOrganizationSetPrimaryView.post called link_id=%s",
            pk,
        )

        instance = get_teacher_organizations_queryset().filter(pk=pk).first()
        if instance is None:
            return Response(
                {"detail": "Связь преподавателя с организацией не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        link = set_primary_teacher_organization(
            teacher=instance.teacher,
            organization=instance.organization,
        )

        return Response(
            TeacherOrganizationSerializer(link).data,
            status=status.HTTP_200_OK,
        )
