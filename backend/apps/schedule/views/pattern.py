from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.schedule.filters import SchedulePatternFilter
from apps.schedule.models import SchedulePattern
from apps.schedule.permissions import (
    CanManageScheduleOrReadOnly,
    ScheduleObjectPermission,
)
from apps.schedule.serializers.pattern import (
    SchedulePatternCopySerializer,
    SchedulePatternSerializer,
)
from apps.schedule.services import (
    copy_patterns_to_period,
    create_pattern,
    deactivate_pattern,
    update_pattern,
)


class SchedulePatternListCreateAPIView(generics.ListCreateAPIView):
    queryset = SchedulePattern.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "week_template",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "course",
        "course_lesson",
    ).prefetch_related("audiences")
    serializer_class = SchedulePatternSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    filterset_class = SchedulePatternFilter
    ordering_fields = ("weekday", "starts_on", "ends_on", "created_at")
    ordering = ("organization", "weekday", "time_slot__number")

    def perform_create(self, serializer) -> None:
        pattern = create_pattern(**serializer.validated_data)
        serializer.instance = pattern


class SchedulePatternDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = SchedulePattern.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "week_template",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "course",
        "course_lesson",
    ).prefetch_related("audiences")
    serializer_class = SchedulePatternSerializer
    permission_classes = [ScheduleObjectPermission]

    def perform_update(self, serializer) -> None:
        pattern = update_pattern(serializer.instance, **serializer.validated_data)
        serializer.instance = pattern


class SchedulePatternDeactivateAPIView(generics.GenericAPIView):
    queryset = SchedulePattern.objects.select_related("organization")
    serializer_class = SchedulePatternSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        pattern = deactivate_pattern(self.get_object())
        serializer = self.get_serializer(pattern)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SchedulePatternCopyAPIView(generics.GenericAPIView):
    serializer_class = SchedulePatternCopySerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patterns = copy_patterns_to_period(**serializer.validated_data)

        response_serializer = SchedulePatternSerializer(patterns, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
