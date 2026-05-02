from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.permissions import IsCourseTeacherOrAdmin
from apps.course.selectors import get_course_module_by_id
from apps.course.serializers import (
    CourseModuleCreateSerializer,
    CourseModuleDetailSerializer,
    CourseModuleListSerializer,
    CourseModuleReorderSerializer,
    CourseModuleUpdateSerializer,
)
from apps.course.services import (
    create_course_module,
    delete_course_module,
    reorder_course_modules,
    update_course_module,
)
from apps.course.views.structure.common import (
    get_course_or_404,
    get_module_or_404,
    validation_error_payload,
)


class CourseModuleListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_or_404(course_pk=course_pk)
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)
        queryset = course.modules.order_by("order", "id")

        serializer = CourseModuleListSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)

        serializer = CourseModuleCreateSerializer(
            data=request.data,
            context={"request": request, "course": course},
        )
        serializer.is_valid(raise_exception=True)

        try:
            module = create_course_module(
                course=course,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc)) from exc

        output_serializer = CourseModuleDetailSerializer(
            module,
            context={"request": request, "course": course},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseModuleDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, module_pk: int):
        module = get_module_or_404(module_pk=module_pk)
        self.check_object_permissions(self.request, module)
        return module

    def get(self, request, module_pk: int, *args, **kwargs):
        module = self.get_object(module_pk)

        serializer = CourseModuleDetailSerializer(
            module,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, module_pk: int, *args, **kwargs):
        module = self.get_object(module_pk)

        serializer = CourseModuleUpdateSerializer(
            module,
            data=request.data,
            partial=True,
            context={"request": request, "module": module},
        )
        serializer.is_valid(raise_exception=True)

        try:
            module = update_course_module(
                module=module,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc)) from exc

        output_serializer = CourseModuleDetailSerializer(
            get_course_module_by_id(module_id=module.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, module_pk: int, *args, **kwargs):
        module = self.get_object(module_pk)

        try:
            delete_course_module(module=module)
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc)) from exc

        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseModuleReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, course_pk: int, *args, **kwargs):
        course = get_course_or_404(course_pk=course_pk)
        self.check_object_permissions(request, course)

        serializer = CourseModuleReorderSerializer(
            data=request.data,
            context={"request": request, "course": course},
        )
        serializer.is_valid(raise_exception=True)

        try:
            reorder_course_modules(
                course=course,
                module_ids_in_order=serializer.validated_data["module_ids_in_order"],
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc)) from exc

        queryset = course.modules.order_by("order", "id")
        output_serializer = CourseModuleListSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
