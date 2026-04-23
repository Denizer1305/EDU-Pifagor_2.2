from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.education.filters import AcademicYearFilter, EducationPeriodFilter
from apps.education.permissions import IsAdminOrReadOnly
from apps.education.selectors import (
    get_academic_years_queryset,
    get_education_periods_queryset,
)
from apps.education.serializers import (
    AcademicYearSerializer,
    EducationPeriodSerializer,
)
from apps.education.services import (
    create_academic_year,
    create_education_period,
    update_academic_year,
    update_education_period,
)


class AcademicYearListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = AcademicYearSerializer
    filterset_class = AcademicYearFilter
    search_fields = (
        "name",
    )
    ordering_fields = (
        "name", "start_date",
        "end_date", "created_at",
    )

    def get_queryset(self):
        return get_academic_years_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        academic_year = create_academic_year(
            name=serializer.validated_data["name"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            description=serializer.validated_data.get("description", ""),
            is_current=serializer.validated_data.get("is_current", False),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(academic_year)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class AcademicYearDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = AcademicYearSerializer

    def get_queryset(self):
        return get_academic_years_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        academic_year = update_academic_year(
            academic_year=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(academic_year)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class EducationPeriodListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EducationPeriodSerializer
    filterset_class = EducationPeriodFilter
    search_fields = (
        "name", "code",
        "academic_year__name",
    )
    ordering_fields = (
        "sequence", "start_date",
        "end_date", "created_at",
    )

    def get_queryset(self):
        return get_education_periods_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        period = create_education_period(
            academic_year=serializer.validated_data["academic_year"],
            name=serializer.validated_data["name"],
            code=serializer.validated_data["code"],
            period_type=serializer.validated_data.get("period_type"),
            sequence=serializer.validated_data.get("sequence", 1),
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            description=serializer.validated_data.get("description", ""),
            is_current=serializer.validated_data.get("is_current", False),
            is_active=serializer.validated_data.get("is_active", True),
        )

        output_serializer = self.get_serializer(period)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class EducationPeriodDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = EducationPeriodSerializer

    def get_queryset(self):
        return get_education_periods_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        period = update_education_period(
            period=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(period)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
