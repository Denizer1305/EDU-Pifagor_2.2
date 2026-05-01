from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.permissions import IsCourseTeacherOrAdmin
from apps.course.selectors import (
    get_course_lesson_by_id,
)
from apps.course.serializers import (
    CourseLessonCreateSerializer,
    CourseLessonDetailSerializer,
    CourseLessonListSerializer,
    CourseLessonMoveSerializer,
    CourseLessonReorderSerializer,
    CourseLessonUpdateSerializer,
)
from apps.course.services import (
    create_course_lesson,
    delete_course_lesson,
    move_course_lesson,
    reorder_course_lessons,
    update_course_lesson,
)
from apps.course.views.structure.common import (
    get_lesson_or_404,
    get_module_or_404,
    validation_error_payload,
)


class CourseLessonListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_module(self, module_pk: int):
        module = get_module_or_404(module_pk=module_pk)
        self.check_object_permissions(self.request, module)
        return module

    def get(self, request, module_pk: int, *args, **kwargs):
        module = self.get_module(module_pk)
        queryset = module.lessons.order_by("order", "id")

        serializer = CourseLessonListSerializer(
            queryset,
            many=True,
            context={"request": request, "module": module},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, module_pk: int, *args, **kwargs):
        module = self.get_module(module_pk)
        course = module.course

        serializer = CourseLessonCreateSerializer(
            data=request.data,
            context={"request": request, "course": course, "module": module},
        )
        serializer.is_valid(raise_exception=True)

        try:
            lesson = create_course_lesson(
                course=course,
                module=module,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseLessonDetailSerializer(
            lesson,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseLessonDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, lesson_pk: int):
        lesson = get_lesson_or_404(lesson_pk=lesson_pk)
        self.check_object_permissions(self.request, lesson)
        return lesson

    def get(self, request, lesson_pk: int, *args, **kwargs):
        lesson = self.get_object(lesson_pk)

        serializer = CourseLessonDetailSerializer(
            lesson,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, lesson_pk: int, *args, **kwargs):
        lesson = self.get_object(lesson_pk)

        serializer = CourseLessonUpdateSerializer(
            lesson,
            data=request.data,
            partial=True,
            context={"request": request, "lesson": lesson},
        )
        serializer.is_valid(raise_exception=True)

        try:
            lesson = update_course_lesson(
                lesson=lesson,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseLessonDetailSerializer(
            get_course_lesson_by_id(lesson_id=lesson.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, lesson_pk: int, *args, **kwargs):
        lesson = self.get_object(lesson_pk)

        try:
            delete_course_lesson(lesson=lesson)
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseLessonMoveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, lesson_pk: int, *args, **kwargs):
        lesson = get_lesson_or_404(lesson_pk=lesson_pk)
        self.check_object_permissions(request, lesson)

        serializer = CourseLessonMoveSerializer(
            data=request.data,
            context={"request": request, "lesson": lesson},
        )
        serializer.is_valid(raise_exception=True)

        target_module = serializer.validated_data["target_module"]

        try:
            lesson = move_course_lesson(
                lesson=lesson,
                target_module=target_module,
                new_order=serializer.validated_data.get("new_order"),
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseLessonDetailSerializer(
            get_course_lesson_by_id(lesson_id=lesson.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CourseLessonReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, module_pk: int, *args, **kwargs):
        module = get_module_or_404(module_pk=module_pk)
        self.check_object_permissions(request, module)

        serializer = CourseLessonReorderSerializer(
            data=request.data,
            context={"request": request, "module": module},
        )
        serializer.is_valid(raise_exception=True)

        try:
            reorder_course_lessons(
                module=module,
                lesson_ids_in_order=serializer.validated_data["lesson_ids_in_order"],
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        queryset = module.lessons.order_by("order", "id")
        output_serializer = CourseLessonListSerializer(
            queryset,
            many=True,
            context={"request": request, "module": module},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
