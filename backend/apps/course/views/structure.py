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
    get_course_by_id,
    get_course_lesson_by_id,
    get_course_material_queryset,
    get_course_module_by_id,
)
from apps.course.serializers import (
    CourseLessonCreateSerializer,
    CourseLessonDetailSerializer,
    CourseLessonListSerializer,
    CourseLessonMoveSerializer,
    CourseLessonReorderSerializer,
    CourseLessonUpdateSerializer,
    CourseMaterialCreateSerializer,
    CourseMaterialDetailSerializer,
    CourseMaterialListSerializer,
    CourseMaterialUpdateSerializer,
    CourseModuleCreateSerializer,
    CourseModuleDetailSerializer,
    CourseModuleListSerializer,
    CourseModuleReorderSerializer,
    CourseModuleUpdateSerializer,
)
from apps.course.services import (
    create_course_lesson,
    create_course_material,
    create_course_module,
    delete_course_lesson,
    delete_course_material,
    delete_course_module,
    move_course_lesson,
    reorder_course_lessons,
    reorder_course_modules,
    update_course_lesson,
    update_course_material,
    update_course_module,
)


class CourseModuleListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_by_id(course_id=course_pk)
        if course is None:
            raise NotFound("Курс не найден.")
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseModuleDetailSerializer(
            module,
            context={"request": request, "course": course},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseModuleDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, module_pk: int):
        module = get_course_module_by_id(module_id=module_pk)
        if module is None:
            raise NotFound("Модуль не найден.")
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseModuleReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, course_pk: int, *args, **kwargs):
        course = get_course_by_id(course_id=course_pk)
        if course is None:
            raise NotFound("Курс не найден.")

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        queryset = course.modules.order_by("order", "id")
        output_serializer = CourseModuleListSerializer(
            queryset,
            many=True,
            context={"request": request, "course": course},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CourseLessonListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_module(self, module_pk: int):
        module = get_course_module_by_id(module_id=module_pk)
        if module is None:
            raise NotFound("Модуль не найден.")
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseLessonDetailSerializer(
            lesson,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseLessonDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, lesson_pk: int):
        lesson = get_course_lesson_by_id(lesson_id=lesson_pk)
        if lesson is None:
            raise NotFound("Урок не найден.")
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseLessonMoveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, lesson_pk: int, *args, **kwargs):
        lesson = get_course_lesson_by_id(lesson_id=lesson_pk)
        if lesson is None:
            raise NotFound("Урок не найден.")

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseLessonDetailSerializer(
            get_course_lesson_by_id(lesson_id=lesson.id),
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CourseLessonReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def post(self, request, module_pk: int, *args, **kwargs):
        module = get_course_module_by_id(module_id=module_pk)
        if module is None:
            raise NotFound("Модуль не найден.")

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        queryset = module.lessons.order_by("order", "id")
        output_serializer = CourseLessonListSerializer(
            queryset,
            many=True,
            context={"request": request, "module": module},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class CourseMaterialListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_course(self, course_pk: int):
        course = get_course_by_id(course_id=course_pk)
        if course is None:
            raise NotFound("Курс не найден.")
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        output_serializer = CourseMaterialDetailSerializer(
            material,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CourseMaterialDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsCourseTeacherOrAdmin)

    def get_object(self, material_pk: int):
        material = CourseMaterial.objects.select_related("course", "lesson").filter(id=material_pk).first()
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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

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
            payload = exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages}
            raise ValidationError(payload)

        return Response(status=status.HTTP_204_NO_CONTENT)
