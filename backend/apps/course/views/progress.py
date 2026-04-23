from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseProgressFilter, LessonProgressFilter
from apps.course.permissions import IsEnrolledStudentOrTeacherOrAdmin
from apps.course.selectors import (
    get_course_enrollment_by_id,
    get_course_progress_by_enrollment_id,
    get_course_progress_queryset,
    get_course_structure_queryset,
    get_lesson_progress_queryset,
)
from apps.course.serializers import (
    CourseProgressDetailSerializer,
    CourseProgressListSerializer,
    CourseProgressStartSerializer,
    LessonProgressCompleteSerializer,
    LessonProgressDetailSerializer,
    LessonProgressListSerializer,
    LessonProgressMarkInProgressSerializer,
)
from apps.course.services import (
    mark_lesson_completed,
    mark_lesson_in_progress,
    start_course_enrollment,
)


def _apply_filterset(filterset_class, request, queryset):
    filterset = filterset_class(
        data=request.query_params,
        queryset=queryset,
    )
    if not filterset.is_valid():
        raise ValidationError(filterset.errors)
    return filterset.qs


class CourseProgressListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = get_course_progress_queryset(
            course_id=request.query_params.get("course_id"),
            student_id=request.query_params.get("student_id"),
        )
        queryset = _apply_filterset(CourseProgressFilter, request, queryset)

        serializer = CourseProgressListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseProgressDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def get(self, request, enrollment_pk: int, *args, **kwargs):
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")

        self.check_object_permissions(request, enrollment)

        progress = get_course_progress_by_enrollment_id(enrollment_id=enrollment.id)
        if progress is None:
            raise NotFound("Прогресс по курсу не найден.")

        serializer = CourseProgressDetailSerializer(
            progress,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseEnrollmentStartAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def post(self, request, enrollment_pk: int, *args, **kwargs):
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")

        self.check_object_permissions(request, enrollment)

        serializer = CourseProgressStartSerializer(
            data=request.data,
            context={"request": request, "enrollment": enrollment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            enrollment = start_course_enrollment(enrollment=enrollment)
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        progress = get_course_progress_by_enrollment_id(enrollment_id=enrollment.id)
        serializer = CourseProgressDetailSerializer(
            progress,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonProgressListAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def get(self, request, enrollment_pk: int, *args, **kwargs):
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")

        self.check_object_permissions(request, enrollment)

        queryset = get_lesson_progress_queryset(enrollment_id=enrollment.id)
        queryset = _apply_filterset(LessonProgressFilter, request, queryset)

        serializer = LessonProgressListSerializer(
            queryset,
            many=True,
            context={"request": request, "enrollment": enrollment},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonProgressMarkInProgressAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def post(self, request, enrollment_pk: int, lesson_pk: int, *args, **kwargs):
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")

        self.check_object_permissions(request, enrollment)

        lesson = get_course_structure_queryset().prefetch_related().first()
        lesson = enrollment.course.lessons.filter(id=lesson_pk).select_related("course", "module").first()
        if lesson is None:
            raise NotFound("Урок не найден.")

        serializer = LessonProgressMarkInProgressSerializer(
            data=request.data,
            context={"request": request, "enrollment": enrollment, "lesson": lesson},
        )
        serializer.is_valid(raise_exception=True)

        try:
            lesson_progress = mark_lesson_in_progress(
                enrollment=enrollment,
                lesson=lesson,
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = LessonProgressDetailSerializer(
            lesson_progress,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class LessonProgressCompleteAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def post(self, request, enrollment_pk: int, lesson_pk: int, *args, **kwargs):
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")

        self.check_object_permissions(request, enrollment)

        lesson = enrollment.course.lessons.filter(id=lesson_pk).select_related("course", "module").first()
        if lesson is None:
            raise NotFound("Урок не найден.")

        serializer = LessonProgressCompleteSerializer(
            data=request.data,
            context={"request": request, "enrollment": enrollment, "lesson": lesson},
        )
        serializer.is_valid(raise_exception=True)

        try:
            lesson_progress = mark_lesson_completed(
                enrollment=enrollment,
                lesson=lesson,
                spent_minutes=serializer.validated_data.get("spent_minutes"),
                score=serializer.validated_data.get("score"),
                attempts_increment=serializer.validated_data.get("attempts_increment", True),
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = LessonProgressDetailSerializer(
            lesson_progress,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
