from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.schedule.filters import ScheduleConflictFilter
from apps.schedule.models import ScheduleConflict, ScheduledLesson, SchedulePattern
from apps.schedule.permissions import (
    CanResolveScheduleConflict,
    ScheduleObjectPermission,
)
from apps.schedule.serializers.conflict import (
    ScheduleConflictDetectPeriodSerializer,
    ScheduleConflictResolveSerializer,
    ScheduleConflictSerializer,
)
from apps.schedule.services import (
    detect_conflicts_for_lesson,
    detect_conflicts_for_pattern,
    detect_conflicts_for_period,
    ignore_conflict,
    resolve_conflict,
)


class ScheduleConflictListAPIView(generics.ListAPIView):
    queryset = ScheduleConflict.objects.select_related(
        "organization",
        "lesson",
        "pattern",
        "teacher",
        "room",
        "group",
        "resolved_by",
    )
    serializer_class = ScheduleConflictSerializer
    permission_classes = [ScheduleObjectPermission]
    filterset_class = ScheduleConflictFilter
    ordering_fields = ("date", "severity", "status", "created_at")
    ordering = ("-severity", "date", "created_at")


class ScheduleConflictDetailAPIView(generics.RetrieveAPIView):
    queryset = ScheduleConflict.objects.select_related(
        "organization",
        "lesson",
        "pattern",
        "teacher",
        "room",
        "group",
        "resolved_by",
    )
    serializer_class = ScheduleConflictSerializer
    permission_classes = [ScheduleObjectPermission]


class ScheduleConflictResolveAPIView(generics.GenericAPIView):
    queryset = ScheduleConflict.objects.select_related("organization")
    serializer_class = ScheduleConflictResolveSerializer
    permission_classes = [CanResolveScheduleConflict]

    def post(self, request, *args, **kwargs):
        conflict = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conflict = resolve_conflict(
            conflict,
            resolved_by=request.user,
            **serializer.validated_data,
        )

        response_serializer = ScheduleConflictSerializer(conflict)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduleConflictIgnoreAPIView(generics.GenericAPIView):
    queryset = ScheduleConflict.objects.select_related("organization")
    serializer_class = ScheduleConflictResolveSerializer
    permission_classes = [CanResolveScheduleConflict]

    def post(self, request, *args, **kwargs):
        conflict = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conflict = ignore_conflict(
            conflict,
            ignored_by=request.user,
            **serializer.validated_data,
        )

        response_serializer = ScheduleConflictSerializer(conflict)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduleConflictDetectLessonAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related(
        "organization",
        "teacher",
        "room",
        "time_slot",
    ).prefetch_related("audiences")
    serializer_class = ScheduleConflictSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        conflicts = detect_conflicts_for_lesson(lesson)

        serializer = self.get_serializer(conflicts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduleConflictDetectPatternAPIView(generics.GenericAPIView):
    queryset = SchedulePattern.objects.select_related(
        "organization",
        "teacher",
        "room",
        "time_slot",
    ).prefetch_related("audiences")
    serializer_class = ScheduleConflictSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        pattern = self.get_object()
        conflicts = detect_conflicts_for_pattern(pattern)

        serializer = self.get_serializer(conflicts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduleConflictDetectPeriodAPIView(generics.GenericAPIView):
    serializer_class = ScheduleConflictDetectPeriodSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = request.user.profile.organization

        conflicts = detect_conflicts_for_period(
            organization=organization,
            starts_on=serializer.validated_data["starts_on"],
            ends_on=serializer.validated_data["ends_on"],
        )

        response_serializer = ScheduleConflictSerializer(conflicts, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
