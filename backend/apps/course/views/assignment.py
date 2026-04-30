from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseAssignmentFilter, CourseEnrollmentFilter
from apps.course.models import CourseAssignment
from apps.course.permissions import (
    IsCourseTeacherOrAdmin,
    IsEnrolledStudentOrTeacherOrAdmin,
)
from apps.course.selectors import (
    get_course_assignments_queryset,
    get_course_by_id,
    get_course_enrollment_by_id,
    get_course_enrollments_queryset,
    get_student_course_enrollments_queryset,
)
from apps.course.serializers import (
    CourseAssignmentCreateSerializer,
    CourseAssignmentDetailSerializer,
    CourseAssignmentListSerializer,
    CourseAssignmentUpdateSerializer,
    CourseEnrollmentDetailSerializer,
    CourseEnrollmentListSerializer,
)
from apps.course.services import (
    assign_course_to_group,
    assign_course_to_student,
    cancel_course_enrollment,
    create_course_enrollment,
    remove_course_assignment,
)


def _apply_filterset(filterset_class, request, queryset):
    filterset = filterset_class(
        data=request.query_params,
        queryset=queryset,
    )
    if not filterset.is_valid():
        raise ValidationError(filterset.errors)
    return filterset.qs


class CourseAssignmentListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_by_id(course_id=course_pk)
        if course is None:
            raise NotFound("Курс не найден.")
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)
        queryset = get_course_assignments_queryset(course_id=course.id)
        queryset = _apply_filterset(CourseAssignmentFilter, request, queryset)

        serializer = CourseAssignmentListSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)

        serializer = CourseAssignmentCreateSerializer(
            data=request.data,
            context={"request": request, "course": course},
        )
        serializer.is_valid(raise_exception=True)

        validated_data = dict(serializer.validated_data)
        assignment_type = validated_data.pop("assignment_type")

        starts_at = validated_data.get("starts_at")
        ends_at = validated_data.get("ends_at")
        is_active = validated_data.get("is_active", True)
        auto_enroll = validated_data.get("auto_enroll", True)
        notes = validated_data.get("notes", "")

        try:
            if assignment_type == CourseAssignment.AssignmentTypeChoices.GROUP:
                assignment = assign_course_to_group(
                    course=course,
                    group=validated_data["group"],
                    assigned_by=request.user,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    is_active=is_active,
                    auto_enroll=auto_enroll,
                    notes=notes,
                )
            else:
                assignment = assign_course_to_student(
                    course=course,
                    student=validated_data["student"],
                    assigned_by=request.user,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    is_active=is_active,
                    auto_enroll=auto_enroll,
                    notes=notes,
                )

                if assignment.auto_enroll and assignment.student_id:
                    create_course_enrollment(
                        course=course,
                        student=assignment.student,
                        assignment=assignment,
                    )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {
                "detail": exc.messages
            }
            raise ValidationError(payload)

        output_serializer = CourseAssignmentDetailSerializer(
            assignment,
            context={"request": request, "course": course},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseAssignmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, assignment_pk: int):
        assignment = get_course_assignments_queryset().filter(id=assignment_pk).first()
        if assignment is None:
            raise NotFound("Назначение не найдено.")
        self.check_object_permissions(self.request, assignment)
        return assignment

    def get(self, request, assignment_pk: int, *args, **kwargs):
        assignment = self.get_object(assignment_pk)
        serializer = CourseAssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, assignment_pk: int, *args, **kwargs):
        assignment = self.get_object(assignment_pk)

        serializer = CourseAssignmentUpdateSerializer(
            assignment,
            data=request.data,
            partial=True,
            context={"request": request, "assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)

        for field_name, value in serializer.validated_data.items():
            setattr(assignment, field_name, value)

        try:
            assignment.full_clean()
            assignment.save()
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {
                "detail": exc.messages
            }
            raise ValidationError(payload)

        output_serializer = CourseAssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, assignment_pk: int, *args, **kwargs):
        assignment = self.get_object(assignment_pk)

        try:
            remove_course_assignment(assignment=assignment)
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {
                "detail": exc.messages
            }
            raise ValidationError(payload)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseEnrollmentListAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_by_id(course_id=course_pk)
        if course is None:
            raise NotFound("Курс не найден.")
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)
        queryset = get_course_enrollments_queryset(course_id=course.id)
        queryset = _apply_filterset(CourseEnrollmentFilter, request, queryset)

        serializer = CourseEnrollmentListSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseEnrollmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsEnrolledStudentOrTeacherOrAdmin)

    def get_object(self, enrollment_pk: int):
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")
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
        enrollment = get_course_enrollment_by_id(enrollment_id=enrollment_pk)
        if enrollment is None:
            raise NotFound("Запись на курс не найдена.")

        self.check_object_permissions(request, enrollment)

        try:
            enrollment = cancel_course_enrollment(enrollment=enrollment)
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {
                "detail": exc.messages
            }
            raise ValidationError(payload)

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
        queryset = _apply_filterset(CourseEnrollmentFilter, request, queryset)

        serializer = CourseEnrollmentListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
