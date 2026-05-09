from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.schedule.filters import ScheduleTimeSlotFilter
from apps.schedule.models import ScheduleTimeSlot
from apps.schedule.permissions import (
    CanManageScheduleOrReadOnly,
    ScheduleObjectPermission,
)
from apps.schedule.serializers.time_slot import (
    ScheduleTimeSlotBulkCreateSerializer,
    ScheduleTimeSlotSerializer,
)
from apps.schedule.services import (
    bulk_create_default_slots,
    create_time_slot,
    update_time_slot,
)


class ScheduleTimeSlotListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScheduleTimeSlot.objects.select_related("organization")
    serializer_class = ScheduleTimeSlotSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    filterset_class = ScheduleTimeSlotFilter
    ordering_fields = ("number", "starts_at", "duration_minutes")
    ordering = ("organization", "education_level", "number")

    def perform_create(self, serializer) -> None:
        slot = create_time_slot(**serializer.validated_data)
        serializer.instance = slot


class ScheduleTimeSlotDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ScheduleTimeSlot.objects.select_related("organization")
    serializer_class = ScheduleTimeSlotSerializer
    permission_classes = [ScheduleObjectPermission]

    def perform_update(self, serializer) -> None:
        slot = update_time_slot(serializer.instance, **serializer.validated_data)
        serializer.instance = slot


class ScheduleTimeSlotBulkCreateAPIView(generics.GenericAPIView):
    serializer_class = ScheduleTimeSlotBulkCreateSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slots = bulk_create_default_slots(**serializer.validated_data)

        response_serializer = ScheduleTimeSlotSerializer(slots, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
