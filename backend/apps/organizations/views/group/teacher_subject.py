from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.filters import TeacherSubjectFilter
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import get_teacher_subjects_queryset
from apps.organizations.serializers import TeacherSubjectSerializer
from apps.organizations.services import (
    assign_teacher_subject,
    remove_teacher_subject,
)

logger = logging.getLogger(__name__)


class TeacherSubjectListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TeacherSubjectSerializer
    filterset_class = TeacherSubjectFilter
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "subject__name",
        "subject__category__name",
    )
    ordering_fields = ("created_at",)

    def get_queryset(self):
        logger.info("TeacherSubjectListView.get_queryset called")
        return get_teacher_subjects_queryset()

    def create(self, request, *args, **kwargs):
        logger.info("TeacherSubjectListView.create called")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        link = assign_teacher_subject(
            teacher=serializer.validated_data["teacher"],
            subject=serializer.validated_data["subject"],
            is_primary=serializer.validated_data.get("is_primary", False),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(link)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TeacherSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TeacherSubjectSerializer

    def get_queryset(self):
        logger.info("TeacherSubjectDetailView.get_queryset called")
        return get_teacher_subjects_queryset()

    def update(self, request, *args, **kwargs):
        logger.info("TeacherSubjectDetailView.update called")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        teacher = serializer.validated_data.get("teacher", instance.teacher)
        subject = serializer.validated_data.get("subject", instance.subject)
        is_primary = serializer.validated_data.get("is_primary", instance.is_primary)
        is_active = serializer.validated_data.get("is_active", instance.is_active)

        link = assign_teacher_subject(
            teacher=teacher,
            subject=subject,
            is_primary=is_primary,
            is_active=is_active,
        )

        output_serializer = self.get_serializer(link)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        logger.info("TeacherSubjectDetailView.patch called")
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info("TeacherSubjectDetailView.destroy called")

        instance = self.get_object()
        remove_teacher_subject(
            teacher=instance.teacher,
            subject=instance.subject,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
