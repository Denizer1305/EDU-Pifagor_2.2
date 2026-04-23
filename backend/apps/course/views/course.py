from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.filters import CourseFilter
from apps.course.models import Course, CourseTeacher
from apps.course.permissions import (
    IsCourseOwnerOrAdmin,
    IsCourseTeacherOrAdmin,
    IsPublishedCourseVisible,
    IsTeacherOrAdmin,
)
from apps.course.selectors import (
    get_course_by_id,
    get_courses_queryset,
    get_public_courses_queryset,
)
from apps.course.serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseDuplicateSerializer,
    CourseListSerializer,
    CoursePublicDetailSerializer,
    CoursePublicListSerializer,
    CourseTeacherCreateSerializer,
    CourseTeacherSerializer,
    CourseTeacherUpdateSerializer,
    CourseUpdateSerializer,
)
from apps.course.services import (
    add_teacher_to_course,
    archive_course,
    create_course,
    duplicate_course,
    publish_course,
    remove_teacher_from_course,
    update_course,
)


def _apply_filterset(filterset_class, request, queryset):
    filterset = filterset_class(
        data=request.query_params,
        queryset=queryset,
    )
    if not filterset.is_valid():
        raise ValidationError(filterset.errors)
    return filterset.qs


class CourseListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        queryset = get_courses_queryset()
        queryset = _apply_filterset(CourseFilter, request, queryset)

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseDetailSerializer(
            course,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, pk: int):
        course = get_course_by_id(course_id=pk)
        if course is None:
            raise NotFound("Курс не найден.")
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
            context={"request": request, "course": course},
        )
        serializer.is_valid(raise_exception=True)

        try:
            course = update_course(
                course=course,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseDetailSerializer(
            get_course_by_id(course_id=course.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CoursePublishAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        course = get_course_by_id(course_id=pk)
        if course is None:
            raise NotFound("Курс не найден.")

        self.check_object_permissions(request, course)

        try:
            course = publish_course(course=course)
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        serializer = CourseDetailSerializer(
            get_course_by_id(course_id=course.id),
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseArchiveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        course = get_course_by_id(course_id=pk)
        if course is None:
            raise NotFound("Курс не найден.")

        self.check_object_permissions(request, course)

        try:
            course = archive_course(course=course)
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        serializer = CourseDetailSerializer(
            get_course_by_id(course_id=course.id),
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseDuplicateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        source_course = get_course_by_id(course_id=pk)
        if source_course is None:
            raise NotFound("Курс не найден.")

        self.check_object_permissions(request, source_course)

        serializer = CourseDuplicateSerializer(
            data=request.data,
            context={"request": request, "source_course": source_course},
        )
        serializer.is_valid(raise_exception=True)

        try:
            new_course = duplicate_course(
                source_course=source_course,
                author=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseDetailSerializer(
            get_course_by_id(course_id=new_course.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseTeacherListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def get_course(self, pk: int):
        course = get_course_by_id(course_id=pk)
        if course is None:
            raise NotFound("Курс не найден.")
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, pk: int, *args, **kwargs):
        course = self.get_course(pk)
        queryset = course.course_teachers.select_related("teacher").order_by("created_at", "id")

        serializer = CourseTeacherSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk: int, *args, **kwargs):
        course = self.get_course(pk)

        serializer = CourseTeacherCreateSerializer(
            data=request.data,
            context={"request": request, "course": course},
        )
        serializer.is_valid(raise_exception=True)

        try:
            teacher_link = add_teacher_to_course(
                course=course,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseTeacherSerializer(
            teacher_link,
            context={"request": request, "course": course},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseTeacherDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseOwnerOrAdmin)

    def get_object(self, course_pk: int, teacher_link_pk: int):
        course = get_course_by_id(course_id=course_pk)
        if course is None:
            raise NotFound("Курс не найден.")

        self.check_object_permissions(self.request, course)

        teacher_link = CourseTeacher.objects.select_related("course", "teacher").filter(
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
            context={"request": request, "course": course, "teacher_link": teacher_link},
        )
        serializer.is_valid(raise_exception=True)

        for field_name, value in serializer.validated_data.items():
            setattr(teacher_link, field_name, value)

        try:
            teacher_link.full_clean()
            teacher_link.save()
        except DjangoValidationError as exc:
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseTeacherSerializer(
            teacher_link,
            context={"request": request, "course": course},
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CoursePublicListAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        queryset = get_public_courses_queryset(
            search=request.query_params.get("q", ""),
            organization_id=request.query_params.get("organization_id"),
        )
        queryset = _apply_filterset(CourseFilter, request, queryset)

        serializer = CoursePublicListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoursePublicDetailAPIView(APIView):
    permission_classes = (AllowAny, IsPublishedCourseVisible)

    def get(self, request, pk: int, *args, **kwargs):
        course = get_course_by_id(course_id=pk)
        if course is None:
            raise NotFound("Курс не найден.")

        self.check_object_permissions(request, course)

        serializer = CoursePublicDetailSerializer(
            course,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
