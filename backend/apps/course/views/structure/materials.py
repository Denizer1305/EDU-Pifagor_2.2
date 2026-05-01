from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models import CourseMaterial
from apps.course.permissions import IsCourseTeacherOrAdmin
from apps.course.selectors import (
    get_course_material_queryset,
)
from apps.course.serializers import (
    CourseMaterialCreateSerializer,
    CourseMaterialDetailSerializer,
    CourseMaterialListSerializer,
    CourseMaterialUpdateSerializer,
)
from apps.course.services import (
    create_course_material,
    delete_course_material,
    update_course_material,
)
from apps.course.views.structure.common import (
    get_course_or_404,
    validation_error_payload,
)


class CourseMaterialListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_or_404(course_pk=course_pk)
        self.check_object_permissions(self.request, course)
        return course

    def get(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)
        lesson_id = request.query_params.get("lesson_id")

        queryset = get_course_material_queryset(
            course_id=course.id,
            lesson_id=int(lesson_id) if lesson_id else None,
        )

        serializer = CourseMaterialListSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, course_pk: int, *args, **kwargs):
        course = self.get_course(course_pk)

        serializer = CourseMaterialCreateSerializer(
            data=request.data,
            context={"request": request, "course": course},
        )
        serializer.is_valid(raise_exception=True)

        try:
            material = create_course_material(
                course=course,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseMaterialDetailSerializer(
            material,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseMaterialDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, material_pk: int):
        material = CourseMaterial.objects.select_related(
            "course",
            "lesson",
        ).filter(id=material_pk).first()

        if material is None:
            raise NotFound("Материал не найден.")

        self.check_object_permissions(self.request, material)
        return material

    def get(self, request, material_pk: int, *args, **kwargs):
        material = self.get_object(material_pk)

        serializer = CourseMaterialDetailSerializer(
            material,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, material_pk: int, *args, **kwargs):
        material = self.get_object(material_pk)

        serializer = CourseMaterialUpdateSerializer(
            material,
            data=request.data,
            partial=True,
            context={"request": request, "material": material},
        )
        serializer.is_valid(raise_exception=True)

        try:
            material = update_course_material(
                material=material,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        output_serializer = CourseMaterialDetailSerializer(
            material,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, material_pk: int, *args, **kwargs):
        material = self.get_object(material_pk)

        try:
            delete_course_material(material=material)
        except DjangoValidationError as exc:
            raise ValidationError(validation_error_payload(exc))

        return Response(status=status.HTTP_204_NO_CONTENT)
