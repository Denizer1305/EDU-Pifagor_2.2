from __future__ import annotations

from rest_framework import generics

from apps.schedule.filters import ScheduleChangeFilter
from apps.schedule.models import ScheduleChange
from apps.schedule.permissions import CanManageScheduleOrReadOnly
from apps.schedule.serializers.change import ScheduleChangeSerializer


class ScheduleChangeListAPIView(generics.ListAPIView):
    queryset = ScheduleChange.objects.select_related(
        "scheduled_lesson",
        "old_room",
        "new_room",
        "old_teacher",
        "new_teacher",
        "changed_by",
    )
    serializer_class = ScheduleChangeSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    filterset_class = ScheduleChangeFilter
    ordering_fields = ("created_at", "change_type", "old_date", "new_date")
    ordering = ("-created_at",)


class ScheduleChangeDetailAPIView(generics.RetrieveAPIView):
    queryset = ScheduleChange.objects.select_related(
        "scheduled_lesson",
        "old_room",
        "new_room",
        "old_teacher",
        "new_teacher",
        "changed_by",
    )
    serializer_class = ScheduleChangeSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
