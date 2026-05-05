from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.schedule.filters import ScheduleCalendarFilter
from apps.schedule.models import ScheduleCalendar, ScheduleWeekTemplate
from apps.schedule.permissions import (
    CanManageScheduleOrReadOnly,
    ScheduleObjectPermission,
)
from apps.schedule.serializers.calendar import (
    ScheduleCalendarMarkSerializer,
    ScheduleCalendarSerializer,
    ScheduleWeekTemplateSerializer,
)
from apps.schedule.services import (
    create_calendar_period,
    mark_holiday,
    mark_practice_period,
    mark_vacation,
)


class ScheduleCalendarListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScheduleCalendar.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
    )
    serializer_class = ScheduleCalendarSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    filterset_class = ScheduleCalendarFilter
    ordering_fields = ("starts_on", "ends_on", "created_at")
    ordering = ("organization", "starts_on")

    def perform_create(self, serializer) -> None:
        calendar = create_calendar_period(**serializer.validated_data)
        serializer.instance = calendar


class ScheduleCalendarDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ScheduleCalendar.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
    )
    serializer_class = ScheduleCalendarSerializer
    permission_classes = [ScheduleObjectPermission]


class ScheduleCalendarMarkHolidayAPIView(generics.GenericAPIView):
    serializer_class = ScheduleCalendarMarkSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calendar = mark_holiday(**serializer.validated_data)

        response_serializer = ScheduleCalendarSerializer(calendar)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduleCalendarMarkVacationAPIView(generics.GenericAPIView):
    serializer_class = ScheduleCalendarMarkSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calendar = mark_vacation(**serializer.validated_data)

        response_serializer = ScheduleCalendarSerializer(calendar)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduleCalendarMarkPracticeAPIView(generics.GenericAPIView):
    serializer_class = ScheduleCalendarMarkSerializer
    permission_classes = [CanManageScheduleOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calendar = mark_practice_period(**serializer.validated_data)

        response_serializer = ScheduleCalendarSerializer(calendar)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduleWeekTemplateListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScheduleWeekTemplate.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
    )
    serializer_class = ScheduleWeekTemplateSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    ordering_fields = ("starts_on", "ends_on", "created_at")
    ordering = ("organization", "starts_on")


class ScheduleWeekTemplateDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ScheduleWeekTemplate.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
    )
    serializer_class = ScheduleWeekTemplateSerializer
    permission_classes = [ScheduleObjectPermission]
