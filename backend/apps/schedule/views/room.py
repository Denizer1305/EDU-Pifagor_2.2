from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.schedule.filters import ScheduleRoomFilter
from apps.schedule.models import ScheduleRoom
from apps.schedule.permissions import (
    CanManageScheduleOrReadOnly,
    ScheduleObjectPermission,
)
from apps.schedule.serializers.room import ScheduleRoomSerializer
from apps.schedule.services import archive_room, create_room, update_room


class ScheduleRoomListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScheduleRoom.objects.select_related("organization", "department")
    serializer_class = ScheduleRoomSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    filterset_class = ScheduleRoomFilter
    search_fields = ("name", "number", "building")
    ordering_fields = ("name", "number", "capacity", "created_at")
    ordering = ("organization", "building", "number")

    def perform_create(self, serializer) -> None:
        room = create_room(**serializer.validated_data)
        serializer.instance = room


class ScheduleRoomDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ScheduleRoom.objects.select_related("organization", "department")
    serializer_class = ScheduleRoomSerializer
    permission_classes = [ScheduleObjectPermission]

    def perform_update(self, serializer) -> None:
        room = update_room(serializer.instance, **serializer.validated_data)
        serializer.instance = room


class ScheduleRoomArchiveAPIView(generics.GenericAPIView):
    queryset = ScheduleRoom.objects.select_related("organization", "department")
    serializer_class = ScheduleRoomSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        room = archive_room(self.get_object())
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
