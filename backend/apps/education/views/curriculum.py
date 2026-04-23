from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.education.filters import CurriculumFilter, CurriculumItemFilter
from apps.education.permissions import IsAdminOrReadOnly
from apps.education.selectors import (
    get_curricula_queryset,
    get_curriculum_items_queryset,
)
from apps.education.serializers import (
    CurriculumItemSerializer,
    CurriculumSerializer,
)
from apps.education.services import (
    create_curriculum,
    create_curriculum_item,
    update_curriculum,
    update_curriculum_item,
)


class CurriculumListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CurriculumSerializer
    filterset_class = CurriculumFilter
    search_fields = (
        "code", "name",
        "organization__name",
        "department__name",
        "academic_year__name",
    )
    ordering_fields = (
        "name", "code",
        "total_hours", "created_at",
    )

    def get_queryset(self):
        return get_curricula_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        curriculum = create_curriculum(
            organization=serializer.validated_data["organization"],
            department=serializer.validated_data.get("department"),
            academic_year=serializer.validated_data["academic_year"],
            code=serializer.validated_data["code"],
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            total_hours=serializer.validated_data.get("total_hours"),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(curriculum)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CurriculumDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CurriculumSerializer

    def get_queryset(self):
        return get_curricula_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        curriculum = update_curriculum(
            curriculum=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(curriculum)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class CurriculumItemListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CurriculumItemSerializer
    filterset_class = CurriculumItemFilter
    search_fields = (
        "curriculum__name",
        "subject__name",
        "subject__short_name",
        "period__name",
    )
    ordering_fields = (
        "sequence", "planned_hours",
        "contact_hours", "independent_hours",
        "created_at",
    )

    def get_queryset(self):
        return get_curriculum_items_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = create_curriculum_item(
            curriculum=serializer.validated_data["curriculum"],
            period=serializer.validated_data["period"],
            subject=serializer.validated_data["subject"],
            sequence=serializer.validated_data.get("sequence", 1),
            planned_hours=serializer.validated_data.get("planned_hours", 0),
            contact_hours=serializer.validated_data.get("contact_hours", 0),
            independent_hours=serializer.validated_data.get("independent_hours", 0),
            assessment_type=serializer.validated_data.get("assessment_type"),
            is_required=serializer.validated_data.get("is_required", True),
            is_active=serializer.validated_data.get("is_active", True),
            notes=serializer.validated_data.get("notes", ""),
        )

        output_serializer = self.get_serializer(item)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CurriculumItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CurriculumItemSerializer

    def get_queryset(self):
        return get_curriculum_items_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        item = update_curriculum_item(
            item=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(item)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
