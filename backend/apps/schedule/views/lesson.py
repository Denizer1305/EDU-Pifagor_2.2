from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.schedule.filters import ScheduledLessonFilter
from apps.schedule.models import ScheduledLesson
from apps.schedule.permissions import (
    CanManageScheduleOrReadOnly,
    CanPublishSchedule,
    ScheduleObjectPermission,
)
from apps.schedule.serializers.lesson import (
    ScheduledLessonChangeRoomSerializer,
    ScheduledLessonReplaceTeacherSerializer,
    ScheduledLessonRescheduleSerializer,
    ScheduledLessonSerializer,
)
from apps.schedule.services import (
    cancel_lesson,
    change_room,
    create_scheduled_lesson,
    lock_lesson,
    publish_lesson,
    replace_teacher,
    reschedule_lesson,
    unlock_lesson,
    update_scheduled_lesson,
)


class ScheduledLessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScheduledLesson.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "pattern",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "course",
        "course_lesson",
        "journal_lesson",
    ).prefetch_related("audiences")
    serializer_class = ScheduledLessonSerializer
    permission_classes = [CanManageScheduleOrReadOnly]
    filterset_class = ScheduledLessonFilter
    ordering_fields = ("date", "starts_at", "ends_at", "created_at")
    ordering = ("date", "starts_at", "time_slot__number")

    def perform_create(self, serializer) -> None:
        lesson = create_scheduled_lesson(**serializer.validated_data)
        serializer.instance = lesson


class ScheduledLessonDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = ScheduledLesson.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "pattern",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "course",
        "course_lesson",
        "journal_lesson",
    ).prefetch_related("audiences")
    serializer_class = ScheduledLessonSerializer
    permission_classes = [ScheduleObjectPermission]

    def perform_update(self, serializer) -> None:
        lesson = update_scheduled_lesson(
            serializer.instance, **serializer.validated_data
        )
        serializer.instance = lesson


class ScheduledLessonPublishAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonSerializer
    permission_classes = [CanPublishSchedule]

    def post(self, request, *args, **kwargs):
        lesson = publish_lesson(self.get_object(), published_by=request.user)
        serializer = self.get_serializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduledLessonCancelAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = cancel_lesson(
            self.get_object(),
            cancelled_by=request.user,
            reason=request.data.get("reason", ""),
        )
        serializer = self.get_serializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduledLessonRescheduleAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonRescheduleSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lesson = reschedule_lesson(
            lesson,
            changed_by=request.user,
            **serializer.validated_data,
        )

        response_serializer = ScheduledLessonSerializer(lesson)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduledLessonReplaceTeacherAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonReplaceTeacherSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lesson = replace_teacher(
            lesson,
            changed_by=request.user,
            **serializer.validated_data,
        )

        response_serializer = ScheduledLessonSerializer(lesson)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduledLessonChangeRoomAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonChangeRoomSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lesson = change_room(
            lesson,
            changed_by=request.user,
            **serializer.validated_data,
        )

        response_serializer = ScheduledLessonSerializer(lesson)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduledLessonLockAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = lock_lesson(self.get_object(), locked_by=request.user)
        serializer = self.get_serializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScheduledLessonUnlockAPIView(generics.GenericAPIView):
    queryset = ScheduledLesson.objects.select_related("organization")
    serializer_class = ScheduledLessonSerializer
    permission_classes = [ScheduleObjectPermission]

    def post(self, request, *args, **kwargs):
        lesson = unlock_lesson(self.get_object(), unlocked_by=request.user)
        serializer = self.get_serializer(lesson)
        return Response(serializer.data, status=status.HTTP_200_OK)
