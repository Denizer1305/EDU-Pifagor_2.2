from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseEnrollmentFilter
from apps.course.permissions import (
    IsCourseTeacherOrAdmin,
    IsEnrolledStudentOrTeacherOrAdmin,
)
from apps.course.selectors import (
    get_course_enrollment_by_id,
    get_course_enrollments_queryset,
    get_student_course_enrollments_queryset,
)
from apps.course.serializers import (
    CourseEnrollmentDetailSerializer,
    CourseEnrollmentListSerializer,
)
from apps.course.services import cancel_course_enrollment
from apps.course.views.assignment.common import (
    apply_filterset,
    get_course_or_404,
    get_enrollment_or_404,
    validation_error_payload,
)


class CourseEnrollmentListAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_or_404(course_pk=course_pk)
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)

        queryset = get_course_enrollments_queryset(course_id=course.id)
        queryset = apply_filterset(CourseEnrollmentFilter, request, queryset)

        serializer = CourseEnrollmentListSerializer(
            queryset,
            many=True,
            context={
                "request": request,
                "course": course,
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseEnrollmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def get_object(self, enrollment_pk: int):
        enrollment = get_enrollment_or_404(enrollment_pk=enrollment_pk)
        self.check_object_permissions(self.request, enrollment)
        return enrollment

    def get(self, request, enrollment_pk: int, *args, **kwargs):
        enrollment = self.get_object(enrollment_pk)

        serializer = CourseEnrollmentDetailSerializer(
            enrollment,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseEnrollmentCancelAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def post(self, request, enrollment_pk: int, *args, **kwargs):
        enrollment = get_enrollment_or_404(enrollment_pk=enrollment_pk)
        self.check_object_permissions(request, enrollment)

        try:
            enrollment = cancel_course_enrollment(enrollment=enrollment)
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        serializer = CourseEnrollmentDetailSerializer(
            get_course_enrollment_by_id(enrollment_id=enrollment.id),
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyCourseEnrollmentListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = get_student_course_enrollments_queryset(
            student_id=request.user.id,
            status=request.query_params.get("status", ""),
        )
        queryset = apply_filterset(CourseEnrollmentFilter, request, queryset)

        serializer = CourseEnrollmentListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
