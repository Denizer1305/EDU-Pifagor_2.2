from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.education.filters import GroupSubjectFilter, TeacherGroupSubjectFilter
from apps.education.permissions import IsAdminOrReadOnly
from apps.education.selectors import (
    get_group_subjects_queryset,
    get_teacher_group_subjects_queryset,
)
from apps.education.serializers import (
    GroupSubjectSerializer,
    TeacherGroupSubjectSerializer,
)
from apps.education.services import (
    assign_teacher_group_subject,
    create_group_subject,
    remove_teacher_group_subject,
    update_group_subject,
)


class GroupSubjectListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GroupSubjectSerializer
    filterset_class = GroupSubjectFilter
    search_fields = (
        "group__name",
        "group__code",
        "subject__name",
        "subject__short_name",
        "academic_year__name",
        "period__name",
    )
    ordering_fields = (
        "planned_hours", "contact_hours",
        "independent_hours", "created_at",
    )

    def get_queryset(self):
        return get_group_subjects_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_subject = create_group_subject(
            group=serializer.validated_data["group"],
            subject=serializer.validated_data["subject"],
            academic_year=serializer.validated_data["academic_year"],
            period=serializer.validated_data["period"],
            planned_hours=serializer.validated_data.get("planned_hours", 0),
            contact_hours=serializer.validated_data.get("contact_hours", 0),
            independent_hours=serializer.validated_data.get("independent_hours", 0),
            assessment_type=serializer.validated_data.get("assessment_type"),
            is_required=serializer.validated_data.get("is_required", True),
            is_active=serializer.validated_data.get("is_active", True),
            notes=serializer.validated_data.get("notes", ""),
        )

        output_serializer = self.get_serializer(group_subject)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class GroupSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = GroupSubjectSerializer

    def get_queryset(self):
        return get_group_subjects_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        group_subject = update_group_subject(
            group_subject=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(group_subject)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class TeacherGroupSubjectListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TeacherGroupSubjectSerializer
    filterset_class = TeacherGroupSubjectFilter
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "group_subject__group__name",
        "group_subject__subject__name",
        "group_subject__academic_year__name",
    )
    ordering_fields = (
        "planned_hours", "starts_at",
        "ends_at", "created_at",
    )

    def get_queryset(self):
        return get_teacher_group_subjects_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignment = assign_teacher_group_subject(
            teacher=serializer.validated_data["teacher"],
            group_subject=serializer.validated_data["group_subject"],
            role=serializer.validated_data.get("role"),
            is_primary=serializer.validated_data.get("is_primary", True),
            is_active=serializer.validated_data.get("is_active", True),
            planned_hours=serializer.validated_data.get("planned_hours", 0),
            starts_at=serializer.validated_data.get("starts_at"),
            ends_at=serializer.validated_data.get("ends_at"),
            notes=serializer.validated_data.get("notes", ""),
        )

        output_serializer = self.get_serializer(assignment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TeacherGroupSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TeacherGroupSubjectSerializer

    def get_queryset(self):
        return get_teacher_group_subjects_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        teacher = serializer.validated_data.get("teacher", instance.teacher)
        group_subject = serializer.validated_data.get("group_subject", instance.group_subject)
        role = serializer.validated_data.get("role", instance.role)
        is_primary = serializer.validated_data.get("is_primary", instance.is_primary)
        is_active = serializer.validated_data.get("is_active", instance.is_active)
        planned_hours = serializer.validated_data.get("planned_hours", instance.planned_hours)
        starts_at = serializer.validated_data.get("starts_at", instance.starts_at)
        ends_at = serializer.validated_data.get("ends_at", instance.ends_at)
        notes = serializer.validated_data.get("notes", instance.notes)

        assignment = assign_teacher_group_subject(
            teacher=teacher,
            group_subject=group_subject,
            role=role,
            is_primary=is_primary,
            is_active=is_active,
            planned_hours=planned_hours,
            starts_at=starts_at,
            ends_at=ends_at,
            notes=notes,
        )

        output_serializer = self.get_serializer(assignment)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        remove_teacher_group_subject(
            teacher=instance.teacher,
            group_subject=instance.group_subject,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
