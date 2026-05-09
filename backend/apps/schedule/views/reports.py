from __future__ import annotations

from rest_framework import generics
from rest_framework.response import Response

from apps.schedule.permissions import CanManageScheduleOrReadOnly
from apps.schedule.selectors.report_selectors import (
    get_group_schedule_report,
    get_room_schedule_report,
    get_teacher_schedule_report,
)
from apps.schedule.serializers.reports import (
    ScheduleGroupReportSerializer,
    ScheduleRoomReportSerializer,
    ScheduleTeacherReportSerializer,
)


class ScheduleGroupReportAPIView(generics.GenericAPIView):
    serializer_class = ScheduleGroupReportSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = get_group_schedule_report(**serializer.validated_data)
        return Response(data)


class ScheduleTeacherReportAPIView(generics.GenericAPIView):
    serializer_class = ScheduleTeacherReportSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = get_teacher_schedule_report(**serializer.validated_data)
        return Response(data)


class ScheduleRoomReportAPIView(generics.GenericAPIView):
    serializer_class = ScheduleRoomReportSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = get_room_schedule_report(**serializer.validated_data)
        return Response(data)
