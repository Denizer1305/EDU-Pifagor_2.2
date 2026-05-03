from __future__ import annotations

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.journal.filters import JournalLessonFilter
from apps.journal.models import JournalLesson
from apps.journal.serializers import (
    JournalLessonCreateSerializer,
    JournalLessonDetailSerializer,
    JournalLessonListSerializer,
    JournalLessonUpdateSerializer,
)


class JournalLessonListCreateAPIView(generics.ListCreateAPIView):
    """Список занятий журнала и создание занятия."""

    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = JournalLessonFilter
    search_fields = (
        "planned_topic",
        "actual_topic",
        "homework",
        "teacher_comment",
        "course__title",
        "group__name",
    )
    ordering_fields = (
        "id",
        "date",
        "lesson_number",
        "created_at",
        "updated_at",
    )
    ordering = ("-date", "-lesson_number", "-id")

    def get_queryset(self):
        return JournalLesson.objects.select_related(
            "course",
            "group",
            "teacher",
            "course_lesson",
        ).order_by("-date", "-lesson_number", "-id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return JournalLessonCreateSerializer
        return JournalLessonListSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        lesson = input_serializer.save()

        output_serializer = JournalLessonDetailSerializer(
            lesson,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class JournalLessonDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление и удаление занятия журнала."""

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return JournalLesson.objects.select_related(
            "course",
            "group",
            "teacher",
            "course_lesson",
        )

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return JournalLessonUpdateSerializer
        return JournalLessonDetailSerializer

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        lesson = self.get_object()

        input_serializer = self.get_serializer(
            lesson,
            data=request.data,
            partial=partial,
        )
        input_serializer.is_valid(raise_exception=True)

        lesson = input_serializer.save()

        output_serializer = JournalLessonDetailSerializer(
            lesson,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data, status=status.HTTP_200_OK)
