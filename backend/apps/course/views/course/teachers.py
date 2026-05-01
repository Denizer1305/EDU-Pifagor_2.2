from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models import CourseTeacher
from apps.course.permissions import IsCourseOwnerOrAdmin
from apps.course.serializers import (
    CourseTeacherCreateSerializer,
    CourseTeacherSerializer,
    CourseTeacherUpdateSerializer,
)
from apps.course.services import (
    add_teacher_to_course,
    remove_teacher_from_course,
)
from apps.course.views.course.common import (
    get_course_or_404,
    validation_error_payload,
)


class CourseTeacherListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def get_course(self, pk: int):
        course = get_course_or_404(course_id=pk)
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, pk: int, *args, **kwargs):
        course = self.get_course(pk)

        queryset = course.course_teachers.select_related("teacher").order_by(
            "created_at",
            "id",
        )

        serializer = CourseTeacherSerializer(
            queryset,
            many=True,
            context={
                "request": request,
                "course": course,
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk: int, *args, **kwargs):
        course = self.get_course(pk)

        serializer = CourseTeacherCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "course": course,
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            teacher_link = add_teacher_to_course(
                course=course,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseTeacherSerializer(
            teacher_link,
            context={
                "request": request,
                "course": course,
            },
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseTeacherDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def get_object(self, course_pk: int, teacher_link_pk: int):
        course = get_course_or_404(course_id=course_pk)
        self.check_object_permissions(self.request, course)

        teacher_link = CourseTeacher.objects.select_related(
            "course",
            "teacher",
        ).filter(
            id=teacher_link_pk,
            course_id=course.id,
        ).first()

        if teacher_link is None:
            raise NotFound("Связь преподавателя с курсом не найдена.")

        return course, teacher_link

    def patch(self, request, course_pk: int, teacher_link_pk: int, *args, **kwargs):
        course, teacher_link = self.get_object(course_pk, teacher_link_pk)

        serializer = CourseTeacherUpdateSerializer(
            teacher_link,
            data=request.data,
            partial=True,
            context={
                "request": request,
                "course": course,
                "teacher_link": teacher_link,
            },
        )
        serializer.is_valid(raise_exception=True)

        for field_name, value in serializer.validated_data.items():
            setattr(teacher_link, field_name, value)

        try:
            teacher_link.full_clean()
            teacher_link.save()
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseTeacherSerializer(
            teacher_link,
            context={
                "request": request,
                "course": course,
            },
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, course_pk: int, teacher_link_pk: int, *args, **kwargs):
        course, teacher_link = self.get_object(course_pk, teacher_link_pk)

        try:
            remove_teacher_from_course(
                course=course,
                teacher=teacher_link.teacher,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        return Response(status=status.HTTP_204_NO_CONTENT)
