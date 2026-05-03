from __future__ import annotations

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.journal.filters import JournalGradeFilter
from apps.journal.models import JournalGrade
from apps.journal.serializers import (
    JournalGradeCreateSerializer,
    JournalGradeDetailSerializer,
    JournalGradeListSerializer,
    JournalGradeUpdateSerializer,
)


class JournalGradeListCreateAPIView(generics.ListCreateAPIView):
    """Список оценок журнала и создание оценки."""

    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = JournalGradeFilter
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
        "grade_type",
        "scale",
        "score_five",
        "weight",
        "created_at",
        "updated_at",
    )
    ordering = ("-lesson__date", "-id")

    def get_queryset(self):
        return JournalGrade.objects.select_related(
            "lesson",
            "lesson__course",
            "lesson__group",
            "student",
            "graded_by",
            "submission",
            "grade_record",
        ).order_by("-lesson__date", "-id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JournalGradeCreateSerializer
        return JournalGradeListSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        grade = input_serializer.save()

        output_serializer = JournalGradeDetailSerializer(
            grade,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class JournalGradeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление и удаление оценки журнала."""

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return JournalGrade.objects.select_related(
            "lesson",
            "lesson__course",
            "lesson__group",
            "student",
            "graded_by",
            "submission",
            "grade_record",
        )

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return JournalGradeUpdateSerializer
        return JournalGradeDetailSerializer

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        grade = self.get_object()

        input_serializer = self.get_serializer(
            grade,
            data=request.data,
            partial=partial,
        )
        input_serializer.is_valid(raise_exception=True)

        grade = input_serializer.save()

        output_serializer = JournalGradeDetailSerializer(
            grade,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data, status=status.HTTP_200_OK)
