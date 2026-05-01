from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.permissions import (
    IsCourseOwnerOrAdmin,
    IsCourseTeacherOrAdmin,
)
from apps.course.selectors import get_course_by_id
from apps.course.serializers import (
    CourseDetailSerializer,
    CourseDuplicateSerializer,
)
from apps.course.services import (
    archive_course,
    duplicate_course,
    publish_course,
)
from apps.course.views.course.common import (
    get_course_or_404,
    validation_error_payload,
)


class CoursePublishAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        course = get_course_or_404(course_id=pk)
        self.check_object_permissions(request, course)

        try:
            course = publish_course(course=course)
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        serializer = CourseDetailSerializer(
            get_course_by_id(course_id=course.id),
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseArchiveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        course = get_course_or_404(course_id=pk)
        self.check_object_permissions(request, course)

        try:
            course = archive_course(course=course)
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        serializer = CourseDetailSerializer(
            get_course_by_id(course_id=course.id),
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseDuplicateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        source_course = get_course_or_404(course_id=pk)
        self.check_object_permissions(request, source_course)

        serializer = CourseDuplicateSerializer(
            data=request.data,
            context={
                "request": request,
                "source_course": source_course,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            new_course = duplicate_course(
                source_course=source_course,
                author=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseDetailSerializer(
            get_course_by_id(course_id=new_course.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
