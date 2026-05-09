from __future__ import annotations

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.journal.filters import AttendanceRecordFilter
from apps.journal.models import AttendanceRecord
from apps.journal.serializers import (
    AttendanceRecordCreateSerializer,
    AttendanceRecordDetailSerializer,
    AttendanceRecordListSerializer,
    AttendanceRecordUpdateSerializer,
)


class AttendanceRecordListCreateAPIView(generics.ListCreateAPIView):
    """Список записей посещаемости и создание записи."""

    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = AttendanceRecordFilter
    search_fields = (
        "comment",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "lesson__planned_topic",
        "lesson__actual_topic",
    )
    ordering_fields = (
        "id",
        "lesson__date",
        "created_at",
        "updated_at",
    )
    ordering = ("-lesson__date", "-id")

    def get_queryset(self):
        return AttendanceRecord.objects.select_related(
            "lesson",
            "lesson__course",
            "lesson__group",
            "student",
        ).order_by("-lesson__date", "-id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AttendanceRecordCreateSerializer
        return AttendanceRecordListSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        attendance = input_serializer.save()

        output_serializer = AttendanceRecordDetailSerializer(
            attendance,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class AttendanceRecordDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление и удаление записи посещаемости."""

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return AttendanceRecord.objects.select_related(
            "lesson",
            "lesson__course",
            "lesson__group",
            "student",
        )

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return AttendanceRecordUpdateSerializer
        return AttendanceRecordDetailSerializer

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        attendance = self.get_object()

        input_serializer = self.get_serializer(
            attendance,
            data=request.data,
            partial=partial,
        )
        input_serializer.is_valid(raise_exception=True)

        attendance = input_serializer.save()

        output_serializer = AttendanceRecordDetailSerializer(
            attendance,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data, status=status.HTTP_200_OK)
