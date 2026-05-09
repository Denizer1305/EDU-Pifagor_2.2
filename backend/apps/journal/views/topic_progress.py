from __future__ import annotations

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models import Course
from apps.journal.filters import TopicProgressFilter
from apps.journal.models import TopicProgress
from apps.journal.serializers import TopicProgressDetailSerializer
from apps.journal.services.topic_progress_services import (
    sync_topic_progress_for_course_group,
)
from apps.organizations.models import Group


class TopicProgressListAPIView(ListAPIView):
    """Список прогресса прохождения тем."""

    permission_classes = (IsAuthenticated,)
    serializer_class = TopicProgressDetailSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = TopicProgressFilter
    ordering_fields = (
        "id",
        "planned_date",
        "actual_date",
        "days_behind",
        "created_at",
        "updated_at",
    )
    ordering = ("planned_date", "id")

    def get_queryset(self):
        return TopicProgress.objects.select_related(
            "course",
            "group",
            "lesson",
            "journal_lesson",
        ).order_by("planned_date", "id")


class TopicProgressSyncInputSerializer(serializers.Serializer):
    """Входные данные для синхронизации прогресса тем."""

    course_id = serializers.IntegerField(min_value=1)
    group_id = serializers.IntegerField(min_value=1)


class TopicProgressSyncAPIView(APIView):
    """Ручная синхронизация прогресса тем по курсу и группе."""

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = TopicProgressSyncInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        course = get_object_or_404(
            Course.objects.all(),
            pk=input_serializer.validated_data["course_id"],
        )
        group = get_object_or_404(
            Group.objects.all(),
            pk=input_serializer.validated_data["group_id"],
        )

        progress_items = sync_topic_progress_for_course_group(
            course=course,
            group=group,
        )

        output_serializer = TopicProgressDetailSerializer(
            progress_items,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "count": len(progress_items),
                "results": output_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
