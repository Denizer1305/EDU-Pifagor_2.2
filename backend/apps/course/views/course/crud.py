from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseFilter
from apps.course.permissions import (
    IsCourseTeacherOrAdmin,
    IsTeacherOrAdmin,
)
from apps.course.selectors import (
    get_course_by_id,
    get_courses_queryset,
)
from apps.course.serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseUpdateSerializer,
)
from apps.course.services import (
    create_course,
    update_course,
)
from apps.course.views.course.common import (
    apply_filterset,
    get_course_or_404,
    validation_error_payload,
)


class CourseListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        queryset = get_courses_queryset()
        queryset = apply_filterset(CourseFilter, request, queryset)

        serializer = CourseListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CourseCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            course = create_course(
                author=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseDetailSerializer(
            course,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, pk: int):
        course = get_course_or_404(course_id=pk)
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, pk: int, *args, **kwargs):
        course = self.get_object(pk)

        serializer = CourseDetailSerializer(
            course,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        course = self.get_object(pk)

        serializer = CourseUpdateSerializer(
            data=request.data,
            partial=True,
            context={
                "request": request,
                "course": course,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            course = update_course(
                course=course,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseDetailSerializer(
            get_course_by_id(course_id=course.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
