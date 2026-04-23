from __future__ import annotations

import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.filters import (
    GroupCuratorFilter,
    GroupFilter,
    TeacherOrganizationFilter,
    TeacherSubjectFilter,
)
from apps.organizations.permissions import IsAdminOrReadOnly
from apps.organizations.selectors import (
    get_group_curators_queryset,
    get_groups_queryset,
    get_teacher_organizations_queryset,
    get_teacher_subjects_queryset,
)
from apps.organizations.serializers import (
    GroupCuratorSerializer,
    GroupJoinCodeSerializer,
    GroupSerializer,
    TeacherOrganizationSerializer,
    TeacherSubjectSerializer,
)
from apps.organizations.services import (
    assign_group_curator,
    assign_teacher_subject,
    assign_teacher_to_organization,
    clear_group_join_code,
    create_group,
    remove_group_curator,
    remove_teacher_from_organization,
    remove_teacher_subject,
    set_group_join_code,
    set_primary_teacher_organization,
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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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


class GroupJoinCodeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info("GroupJoinCodeView.post called group_id=%s", pk)
        group = get_groups_queryset().filter(pk=pk).first()
        if group is None:
            return Response({"detail": "Группа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GroupJoinCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = set_group_join_code(
            group=group,
            raw_code=serializer.validated_data["join_code"],
            expires_at=serializer.validated_data.get("join_code_expires_at"),
        )

        return Response(
            GroupSerializer(group).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk, *args, **kwargs):
        logger.info("GroupJoinCodeView.delete called group_id=%s", pk)
        group = get_groups_queryset().filter(pk=pk).first()
        if group is None:
            return Response({"detail": "Группа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        group = clear_group_join_code(group=group)
        return Response(
            GroupSerializer(group).data,
            status=status.HTTP_200_OK,
        )


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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        teacher = serializer.validated_data.get("teacher", instance.teacher)
        organization = serializer.validated_data.get("organization", instance.organization)
        position = serializer.validated_data.get("position", instance.position)
        employment_type = serializer.validated_data.get("employment_type", instance.employment_type)
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
        logger.info("TeacherOrganizationSetPrimaryView.post called link_id=%s", pk)
        instance = get_teacher_organizations_queryset().filter(pk=pk).first()
        if instance is None:
            return Response({"detail": "Связь преподавателя с организацией не найдена."}, status=status.HTTP_404_NOT_FOUND)

        link = set_primary_teacher_organization(
            teacher=instance.teacher,
            organization=instance.organization,
        )

        return Response(
            TeacherOrganizationSerializer(link).data,
            status=status.HTTP_200_OK,
        )


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

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
